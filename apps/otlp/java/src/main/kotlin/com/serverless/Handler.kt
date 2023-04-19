package com.serverless

import com.amazonaws.services.lambda.runtime.Context
import com.amazonaws.services.lambda.runtime.RequestHandler

class Handler:RequestHandler<Map<String, Any>, ApiGatewayResponse> {
  override fun handleRequest(input:Map<String, Any>, context:Context):ApiGatewayResponse {
    return ApiGatewayResponse.build {
      statusCode = 200
      objectBody = HelloResponse("Go Serverless v1.x! Your Kotlin function executed successfully!", input)
      headers = mapOf("X-Powered-By" to "AWS Lambda & serverless")
    }
  }
}
