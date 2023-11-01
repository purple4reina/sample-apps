package example;

import java.io.*;
import java.net.*;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPEvent;
import com.amazonaws.services.lambda.runtime.events.APIGatewayV2HTTPResponse;
import org.json.JSONObject;

import static example.Context.currentTraceId;
import static example.Context.runtime;

public class Client implements RequestHandler<APIGatewayV2HTTPEvent, APIGatewayV2HTTPResponse>{

  private static final String[] serverUrls = System.getenv("SERVER_URLS").split(",");

  @Override
  public APIGatewayV2HTTPResponse handleRequest(APIGatewayV2HTTPEvent event, Context context)
  {
    final String data = new JSONObject()
      .put("runtime", runtime)
      .put("trace_id", currentTraceId())
      .toString();

    for (String url : serverUrls) {
        try {
            System.out.println("calling " + url + " with data " + data);
            URLConnection conn = new URL(url).openConnection();
            conn.getOutputStream().write(data.getBytes("UTF-8"));
            InputStream response = conn.getInputStream();
        } catch (IOException e) {}
    }

    APIGatewayV2HTTPResponse response = new APIGatewayV2HTTPResponse();
    response.setStatusCode(200);
    response.setBody("ok");
    return response;
  }
}
