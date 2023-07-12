package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.SQSEvent;

public class Consumer implements RequestHandler<SQSEvent, Void>{

  @Override
  public Void handleRequest(SQSEvent event, Context context)
  {
    for (SQSEvent.SQSMessage message : event.getRecords()) {
      System.out.println(message.getBody());
    }
    return null;
  }
}
