package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPResponse;

import software.amazon.awssdk.services.lambda.LambdaClient;
import software.amazon.awssdk.services.lambda.model.InvokeRequest;
import software.amazon.awssdk.core.SdkBytes;

// Handler value: example.Handler
public class Handler implements RequestHandler<APIGatewayV2HTTPEvent, APIGatewayV2HTTPResponse>{

  private final boolean IS_CLIENT = System.getenv("IS_CLIENT") != null;
  private final String FUNCTION_NAME = System.getenv("DOWNSTREAM_FUNCTION_NAME");

  @Override
  public APIGatewayV2HTTPResponse handleRequest(APIGatewayV2HTTPEvent event, Context context)
  {
    System.out.println(String.format("IS_CLIENT: %s", IS_CLIENT));
    System.out.println(String.format("context.getClientContext(): %s", context.getClientContext()));

    if (IS_CLIENT) {
      LambdaClient lambdaClient = LambdaClient.builder().build();
      InvokeRequest request = InvokeRequest.builder()
        .functionName(FUNCTION_NAME)
        .payload(SdkBytes.fromString("{\"hello\":\"world\"}", java.nio.charset.StandardCharsets.UTF_8))
        .invocationType("Event")
        .build();
      lambdaClient.invoke(request);
    }

    APIGatewayV2HTTPResponse response = new APIGatewayV2HTTPResponse();
    response.setStatusCode(200);
    response.setBody("ok");
    return response;
  }
}
