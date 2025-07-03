package com.example.analizardeimagenesonline

import android.Manifest
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.camera.view.PreviewView
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLifecycleOwner
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.lifecycle.viewmodel.compose.viewModel
import com.google.accompanist.permissions.ExperimentalPermissionsApi
import com.google.accompanist.permissions.PermissionStatus
import com.google.accompanist.permissions.rememberPermissionState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Slider
import androidx.compose.foundation.layout.Arrangement
import com.example.analizardeimagenesonline.cattleDetails
import androidx.compose.ui.graphics.asImageBitmap
import android.graphics.BitmapFactory
import androidx.compose.foundation.Image


class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                val vm: RecognitionViewModel = viewModel()
                CameraScreen(vm)
            }
        }


    }
}

@OptIn(ExperimentalPermissionsApi::class)
@Composable
fun CameraScreen(vm: RecognitionViewModel) {
    val cameraPermissionState = rememberPermissionState(Manifest.permission.CAMERA)

    // Solicita el permiso apenas arranque
    LaunchedEffect(Unit) {
        cameraPermissionState.launchPermissionRequest()
    }

    when (val status = cameraPermissionState.status) {
        PermissionStatus.Granted -> CameraPreviewWithControls(vm)
        is PermissionStatus.Denied -> {
            if (status.shouldShowRationale) {
                Text(
                    text = "Necesito permiso de cámara para funcionar",
                    modifier = Modifier
                        .fillMaxSize()
                        .wrapContentSize(Alignment.Center)
                )
            } else {
                Text(
                    text = "Por favor activa el permiso de cámara desde Ajustes",
                    modifier = Modifier
                        .fillMaxSize()
                        .wrapContentSize(Alignment.Center)
                )
            }
        }
    }
}
@Composable
fun CameraPreviewWithControls(vm: RecognitionViewModel) {
    var recognizing by remember { mutableStateOf(false) }
    // Estado local para saber si la cámara corre
    var running by remember { mutableStateOf(false) }
    var isCameraRunning by remember { mutableStateOf(false) }
    val isProcessing by vm::isProcessingState

    // Umbral de confianza, en rango 0f..1f
    var thresholdPercent by remember { mutableStateOf(40) } // entre 0 y 100
    val threshold = thresholdPercent / 100f

    // Texto de resultado proveniente del ViewModel
    val result by remember { vm::resultText }
    val predictedBreed = vm.predictedClass
    val breedInfo = cattleDetails[predictedBreed]
    val imageBytes = vm.capturedImage
    val bitmap = remember(imageBytes) {
        imageBytes?.let {
            BitmapFactory.decodeByteArray(it, 0, it.size)?.asImageBitmap()
        }
    }
    var limpiarEnabled by remember { mutableStateOf(false) } // <--- empieza desactivado


    // Contexto y previewView
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val previewView = remember { PreviewView(context) }

    Box(Modifier.fillMaxSize()) {
        // 1️⃣ Vista previa de cámara
        AndroidView(factory = { previewView }, Modifier.fillMaxSize())

        // 2️⃣ Texto de resultado
        Text(
            text = result,
            color = Color.White,
            fontSize = 20.sp,
            modifier = Modifier
                .align(Alignment.TopCenter)
                .background(Color.Black.copy(alpha = 0.5f))
                .padding(8.dp)
        )
        if (breedInfo != null && bitmap != null) {
            Column(
                modifier = Modifier
                    .align(Alignment.Center)
                    .padding(16.dp)
                    .background(Color.White.copy(alpha = 0.95f), RoundedCornerShape(16.dp))
                    .padding(16.dp),
                verticalArrangement = Arrangement.spacedBy(8.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                Image(
                    bitmap = bitmap,
                    contentDescription = "Imagen capturada",
                    modifier = Modifier
                        .size(250.dp)
                        .background(Color.LightGray, RoundedCornerShape(8.dp))
                )
                Text("Raza: ${breedInfo.name}", fontSize = 20.sp, color = Color.Black)
                Text("Descripción: ${breedInfo.description}", color = Color.DarkGray)
                Text("Peso promedio: ${breedInfo.averageWeightKg}", color = Color.DarkGray)
                Text("Altura promedio: ${breedInfo.averageHeightCm}", color = Color.DarkGray)
                Text("País de origen: ${breedInfo.originCountry}", color = Color.DarkGray)
                Text("Color de pelaje: ${breedInfo.coatColor}", color = Color.DarkGray)
                Text("Cuernos: ${breedInfo.hornStatus}", color = Color.DarkGray)
                Text("Temperamento: ${breedInfo.temperament}", color = Color.DarkGray)
                Text("Propósito: ${breedInfo.purpose}", color = Color.DarkGray)
                Text("Adaptabilidad: ${breedInfo.climateAdaptability}", color = Color.DarkGray)
            }
        }


        // 3️⃣ Slider de umbral
        Column(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(horizontal = 16.dp, vertical = 80.dp)
                .background(Color.Black.copy(alpha = 0.4f), shape = RoundedCornerShape(8.dp))
                .padding(8.dp)
        ) {
            Text("Umbral de confianza: $thresholdPercent%", color = Color.White)
            Slider(
                value = thresholdPercent.toFloat(),
                onValueChange = { thresholdPercent = it.toInt() },
                valueRange = 0f..100f,
                steps = 100,
                modifier = Modifier.fillMaxWidth()
            )
        }


        // 4️⃣ Botones de controlar cámara
        Row(
            horizontalArrangement = Arrangement.spacedBy(12.dp),
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(16.dp)
        ) {
            Button(
                onClick = { vm.startContinuousRecognition(threshold)
                },
                enabled = isCameraRunning && !isProcessing
            ) {
                Text("Reconocer")
            }

            Button(onClick = {
                if (!isCameraRunning) {
                    vm.startCamera(previewView, lifecycleOwner)
                } else {
                    vm.stopCamera()
                }
                isCameraRunning = !isCameraRunning
                vm.clearPrediction()
                vm.clearCapturedImage()
                vm.updateResultText("Presione Iniciar")



            }) {
                Text(if (isCameraRunning) "Detener" else "Iniciar")
            }
            Button(
                onClick = {
                    vm.clearAll()
                    limpiarEnabled = false // lo desactivas después de limpiar, si quieres
                },
                enabled = limpiarEnabled // <-- aquí usas la variable
            ) {
                Text("Limpiar")
            }

        }
    }
    LaunchedEffect(result) {
        recognizing = false
    }
    LaunchedEffect(vm.capturedImage, vm.predictedClass) {
        limpiarEnabled = vm.capturedImage != null || !vm.predictedClass.isNullOrEmpty()
    }






}

