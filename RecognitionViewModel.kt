package com.example.analizardeimagenesonline
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.core.ImageAnalysis
import android.app.Application
import android.graphics.ImageFormat
import android.graphics.Rect
import android.graphics.YuvImage
import android.util.Log
import androidx.camera.core.*
import androidx.camera.view.PreviewView
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.getValue
import androidx.compose.runtime.setValue
import androidx.core.content.ContextCompat
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.LifecycleOwner
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import okhttp3.MultipartBody
import java.io.ByteArrayOutputStream
import java.util.concurrent.Executors


class RecognitionViewModel(app: Application) : AndroidViewModel(app) {


    /** Raza predicha tras un reconocimiento exitoso (o null si no hay). */
    var predictedClass by mutableStateOf<String?>(null)
        private set

    /** Indica a la UI si hay una petición/polling en curso. */
    var isProcessingState by mutableStateOf(false)
        private set

    /** ByteArray del último frame aceptado, para mostrar su bitmap en pantalla. */
    var capturedImage by mutableStateOf<ByteArray?>(null)
        private set

    /** Texto que se muestra arriba con el estado o resultado actual. */
    var resultText by mutableStateOf("Presione Iniciar")
        private set

    /** Marca si estamos en modo de reconocimiento continuo (streaming de frames). */
    var recognizing by mutableStateOf(false)

    // ── Campos internos para CameraX y control ───────────────────────────

    /** Caso de uso para capturar una sola imagen (ImageCapture.takePicture()). */
    private var imageCapture: ImageCapture? = null

    /** Proveedor que vincula los casos de uso (preview, analysis, capture). */
    private lateinit var cameraProvider: ProcessCameraProvider

    /** Caso de uso de análisis de imagen para recibir frames en streaming. */
    private var analysisUseCase: ImageAnalysis? = null

        // ── Flags de control de concurrencia y parámetros ────────────────────

    /** Flag interno que evita solapar múltiples corrutinas de polling. */
    private var isProcessing = false

    /** Umbral (0f..1f) fijado al pulsar “Reconocer”, usado en processWithPolling. */
    private var desiredThreshold = 0f


    // 1) Cambia la firma para recibir también el LifecycleOwner
    fun startCamera(previewView: PreviewView, lifecycleOwner: LifecycleOwner) {
        val ctx = getApplication<Application>()
        val cameraProviderFuture = ProcessCameraProvider.getInstance(ctx)
        cameraProviderFuture.addListener({
            cameraProvider = cameraProviderFuture.get()
            val preview = Preview.Builder().build().also {
                it.setSurfaceProvider(previewView.surfaceProvider)
            }
            analysisUseCase = ImageAnalysis.Builder()
                .setBackpressureStrategy(ImageAnalysis.STRATEGY_KEEP_ONLY_LATEST)
                .build().also { ana ->
                    ana.setAnalyzer(Executors.newSingleThreadExecutor()) { image ->
                              if (recognizing) {
                                      processImageProxy(image)
                                  } else {
                                       image.close()
                                   }
                           }
                }
            imageCapture = ImageCapture.Builder().build()
            cameraProvider.unbindAll()
            // 2) Usa el lifecycleOwner que te pasan en lugar de castear el Application
            cameraProvider.bindToLifecycle(
                lifecycleOwner,
                CameraSelector.DEFAULT_BACK_CAMERA,
                preview,
                analysisUseCase,
                imageCapture

            )
        }, ContextCompat.getMainExecutor(ctx))
    }


    private fun processImageProxy(image: ImageProxy) {
        if (isProcessing) {
            image.close()
            return
        }
        isProcessing = true
        isProcessingState = true

        // Convierte a JPEG y dispara el polling
        val jpeg = image.toJpegByteArray()
        image.close()
        processWithPolling(jpeg, desiredThreshold)
    }



    fun startContinuousRecognition(threshold: Float) {
        
        desiredThreshold = threshold
        recognizing = true
        resultText = "Analizando…"
    }

    private suspend fun updateResultOnMain(text: String) {
        withContext(Dispatchers.Main) {
            resultText = text
        }
    }

    fun ImageProxy.toJpegByteArray(quality: Int = 90): ByteArray {
        // Si viene ya en JPEG, sólo lee el único plano
        if (format == ImageFormat.JPEG || planes.size == 1) {
            val buffer = planes[0].buffer
            return ByteArray(buffer.remaining()).also { buffer.get(it) }
        }

        // Si fuera realmente YUV_420_888…
        val yBuffer = planes[0].buffer
        val uBuffer = planes[1].buffer
        val vBuffer = planes[2].buffer
        val ySize = yBuffer.remaining()
        val uSize = uBuffer.remaining()
        val vSize = vBuffer.remaining()

        // NV21 = [Y][V][U]
        val nv21 = ByteArray(ySize + uSize + vSize).apply {
            yBuffer.get(this, 0, ySize)
            vBuffer.get(this, ySize, vSize)
            uBuffer.get(this, ySize + vSize, uSize)
        }

        val yuv = YuvImage(nv21, ImageFormat.NV21, width, height, null)
        return ByteArrayOutputStream().use { out ->
            yuv.compressToJpeg(Rect(0, 0, width, height), quality, out)
            out.toByteArray()
        }
    }
    /** Detiene el análisis de frames y libera la cámara */
    fun stopCamera() {
        analysisUseCase?.clearAnalyzer()
        if (::cameraProvider.isInitialized) {
            cameraProvider.unbindAll()
        }
    }
    private fun processWithPolling(
        jpegBytes: ByteArray,
        threshold: Float
    ) {
        val part = MultipartBody.Part.createFormData(
            "file", "frame.jpg",
            jpegBytes.toRequestBody("image/jpeg".toMediaType())
        )
        viewModelScope.launch(Dispatchers.IO) {
            try {
                // 1️⃣ Envío inicial
                val submitResp = RetrofitClient.api.submitImage(part)
                if (!submitResp.isSuccessful) {
                    updateResultOnMain("Error submit: ${submitResp.code()}")
                    return@launch
                }
                val jobId = submitResp.body()?.job_id
                    ?: throw Exception("No job_id")

                // 2️⃣ Polling
                while (true) {
                    delay(15_000L)
                    val statusResp = RetrofitClient.api.getJobStatus(jobId)
                    if (!statusResp.isSuccessful) {
                        updateResultOnMain("Error status: ${statusResp.code()}")
                        break
                    }
                    val job = statusResp.body()!!
                    when (job.status) {
                        "pending" -> updateResultOnMain("Procesando…")
                        "done" -> {
                            val score = job.score ?: 0f

                            if (score >= threshold) {
                                // Éxito: muestro resultado y detengo el reconocimiento continuo
                                updateResultOnMain("${job.`class`!!.uppercase()} (${(score * 100).toInt()}%)")
                                withContext(Dispatchers.Main) {
                                              // Clase descubierta
                                               predictedClass = job.`class`!!
                                               // El último frame enviado
                                               capturedImage = jpegBytes
                                           }
                                recognizing = false
                                break
                                // Si quieres, detén también el analizador:
                                // analysisUseCase?.clearAnalyzer()
                            } else {
                                // Confianza baja: libero isProcessing para que el siguiente frame
                                // (que ya está llegando) dispare otro processImageProxy()
                                // y vuelva a llamar a processWithPolling automáticamente.
                                updateResultOnMain("Confianza baja: ${(score*100).toInt()}%, reintentando…")
                                return@launch
                            }
                        }

                        "error" -> {
                            val msg = job.detail ?: "Desconocido"
                            updateResultOnMain("Error server: $msg")
                            break
                        }
                    }
                }
            } catch (e: Exception) {
                updateResultOnMain("Excepción: ${e.message}")
            } finally {
                isProcessing = false
                isProcessingState = false

            }
        }
    }


    fun clearAll() {
        predictedClass = null
        capturedImage = null
        resultText = "..."
        recognizing=false
        analysisUseCase?.clearAnalyzer()
    }
    fun clearPrediction() {
        predictedClass = null
    }
    fun clearCapturedImage() {
        capturedImage = null
    }
    fun updateResultText(text: String) {
        resultText = text
    }

}
/*
fun captureAndRecognize(threshold: Float) {
    if (isProcessing) return
    isProcessing = true
    isProcessingState = true

    viewModelScope.launch(Dispatchers.Main) {
        resultText = "Capturando…"
    }

    val ic = imageCapture
    if (ic == null) {
        viewModelScope.launch(Dispatchers.Main) {
            resultText = "Cámara no inicializada"
        }
        isProcessing = false
        isProcessingState = false

        return
    }

    ic.takePicture(
        ContextCompat.getMainExecutor(getApplication()),
        object : ImageCapture.OnImageCapturedCallback() {
            override fun onCaptureSuccess(image: ImageProxy) {
                // Convertimos a JPEG y lanzamos el polling
                val jpeg = image.toJpegByteArray()
                capturedImage = jpeg  // 👈 Guardamos la imagen para mostrar
                image.close()
                processWithPolling(jpeg, threshold)
            }

            override fun onError(exc: ImageCaptureException) {
                viewModelScope.launch(Dispatchers.Main) {
                    resultText = "Error captura: ${exc.message}"
                }
                isProcessing = false
                isProcessingState = false

            }
        }
    )
}
// */