// ApiService.kt (antes filecite turn0file0)
package com.example.analizardeimagenesonline

import okhttp3.MultipartBody
import retrofit2.Response
import retrofit2.http.*

data class SubmitResponse(val job_id: String)
data class JobStatus(
    val status: String,
    val `class`: String? = null,
    val score: Float? = null,
    val detail: String? = null
)

interface ApiService {
    @Multipart
    @POST("predict-image")
    suspend fun submitImage(
        @Part file: MultipartBody.Part
    ): Response<SubmitResponse>

    @GET("predict-status/{job_id}")
    suspend fun getJobStatus(
        @Path("job_id") jobId: String
    ): Response<JobStatus>
}
