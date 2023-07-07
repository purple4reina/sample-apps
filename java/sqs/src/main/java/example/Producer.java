package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPResponse;

import com.amazonaws.services.sqs.AmazonSQS;
import com.amazonaws.services.sqs.AmazonSQSClientBuilder;
import com.amazonaws.services.sqs.model.SendMessageRequest;

// Handler value: example.Handler
public class Producer implements RequestHandler<APIGatewayV2HTTPEvent, APIGatewayV2HTTPResponse>{

  final AmazonSQS sqs = AmazonSQSClientBuilder.defaultClient();
  final String queueUrl = System.getenv("QUEUE_URL");

  @Override
  public APIGatewayV2HTTPResponse handleRequest(APIGatewayV2HTTPEvent event, Context context)
  {

    SendMessageRequest request = new SendMessageRequest()
      .withQueueUrl(queueUrl)
      .withMessageBody("hello world");
    sqs.sendMessage(request);

    APIGatewayV2HTTPResponse response = new APIGatewayV2HTTPResponse();
    response.setStatusCode(200);
    response.setBody("ok");
    return response;
  }
}
