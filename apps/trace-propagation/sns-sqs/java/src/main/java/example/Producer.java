package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPResponse;
import org.json.JSONObject;
import software.amazon.awssdk.services.sns.SnsClient;
import software.amazon.awssdk.services.sns.model.PublishRequest;

import static example.Context.currentTraceId;
import static example.Context.runtime;

public class Producer implements RequestHandler<APIGatewayV2HTTPEvent, APIGatewayV2HTTPResponse>{

  private static final SnsClient client = SnsClient.builder().build();
  private static final String[] topicArns = System.getenv("SNS_TOPIC_ARNS").split(",");

  @Override
  public APIGatewayV2HTTPResponse handleRequest(APIGatewayV2HTTPEvent event, Context context)
  {
    final String msg = new JSONObject()
      .put("runtime", runtime)
      .put("trace_id", currentTraceId())
      .toString();

    for (String arn : topicArns) {
        System.out.println("sending sns-sqs message " + msg + " to " + arn);
        PublishRequest request = PublishRequest.builder()
            .message(msg)
            .topicArn(arn)
            .build();
        client.publish(request);
    }

    APIGatewayV2HTTPResponse response = new APIGatewayV2HTTPResponse();
    response.setStatusCode(200);
    response.setBody("ok");
    return response;
  }
}
