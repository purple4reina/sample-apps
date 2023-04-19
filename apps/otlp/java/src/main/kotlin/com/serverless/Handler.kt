package com.serverless

import com.amazonaws.services.lambda.runtime.Context
import com.amazonaws.services.lambda.runtime.RequestHandler

class Handler:RequestHandler<Map<String, Any>, ApiGatewayResponse> {
  override fun handleRequest(input:Map<String, Any>, context:Context):ApiGatewayResponse {
    return ApiGatewayResponse.build {
      statusCode = 200
      objectBody = HelloResponse("{\"cold_start\":true,\"language\":\"java\"}")
    }
  }
}
