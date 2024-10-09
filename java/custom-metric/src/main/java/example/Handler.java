package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPResponse;

import com.timgroup.statsd.NonBlockingStatsDClientBuilder;
import com.timgroup.statsd.StatsDClient;

// Handler value: example.Handler
public class Handler implements RequestHandler<APIGatewayV2HTTPEvent, APIGatewayV2HTTPResponse>{

  private static final StatsDClient Statsd = new NonBlockingStatsDClientBuilder()
    .hostname("localhost")
    .build();

  static {
    Runtime.getRuntime().addShutdownHook(new Thread() {
      @Override
      public void run() {
        System.out.println("[runtime] shutdownHook triggered");
        try {
          Thread.sleep(300);
        } catch (InterruptedException e) {
          System.out.println("[runtime] sleep interrupted");
        }
        System.out.println("[runtime] exiting");
      }
    });
  }

  @Override
  public APIGatewayV2HTTPResponse handleRequest(APIGatewayV2HTTPEvent event, Context context)
  {
    Statsd.recordDistributionValue("rey.custom.java", 1, new String[]{"color:purple"});

    APIGatewayV2HTTPResponse response = new APIGatewayV2HTTPResponse();
    response.setStatusCode(200);
    response.setBody("ok");
    return response;
  }
}
