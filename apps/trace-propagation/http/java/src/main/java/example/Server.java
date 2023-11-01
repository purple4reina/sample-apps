package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPResponse;
import com.timgroup.statsd.NonBlockingStatsDClientBuilder;
import com.timgroup.statsd.StatsDClient;
import org.json.JSONObject;

import static example.Context.currentTraceId;
import static example.Context.runtime;

public class Server implements RequestHandler<APIGatewayV2HTTPEvent, APIGatewayV2HTTPResponse>{

  private static final StatsDClient statsd = new NonBlockingStatsDClientBuilder().hostname("localhost").build();

  @Override
  public APIGatewayV2HTTPResponse handleRequest(APIGatewayV2HTTPEvent event, Context context)
  {
    String traceId = currentTraceId();
    String payload = event.getBody();
    System.out.println("received http data " + payload);

    JSONObject parsed = new JSONObject(payload);
    statsd.recordDistributionValue("trace_context.propagated.http", 1, new String[]{
      "client_runtime:" + runtime,
      "server_runtime:" + parsed.optString("runtime"),
      parsed.optString("trace_id").equals(traceId) ? "success:true" : "success:false",
      "transport:http",
    });

    APIGatewayV2HTTPResponse response = new APIGatewayV2HTTPResponse();
    response.setStatusCode(200);
    response.setBody("ok");
    return response;
  }
}
