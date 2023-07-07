package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPResponse;
import com.amazonaws.services.sqs.AmazonSQS;
import com.amazonaws.services.sqs.AmazonSQSClientBuilder;
import com.amazonaws.services.sqs.model.Message;
import com.amazonaws.services.sqs.model.SendMessageRequest;
import java.util.List;

// Handler value: example.Handler
public class Consumer implements RequestHandler<APIGatewayV2HTTPEvent, APIGatewayV2HTTPResponse>{

  final AmazonSQS sqs = AmazonSQSClientBuilder.defaultClient();
  final String queueUrl = System.getenv("QUEUE_URL");

  @Override
  public APIGatewayV2HTTPResponse handleRequest(APIGatewayV2HTTPEvent event, Context context)
  {
    List<Message> messages = sqs.receiveMessage(queueUrl).getMessages();

    for (Message m : messages) {
      sqs.deleteMessage(queueUrl, m.getReceiptHandle());
    }

    APIGatewayV2HTTPResponse response = new APIGatewayV2HTTPResponse();
    response.setStatusCode(200);
    response.setBody("ok");
    return response;
  }
}
