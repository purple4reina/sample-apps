package example;

import com.amazonaws.services.lambda.runtime.Context;
import com.amazonaws.services.lambda.runtime.RequestHandler;
import com.amazonaws.services.lambda.runtime.events.SQSEvent;
import com.amazonaws.services.lambda.runtime.events.SQSBatchResponse;
import com.timgroup.statsd.NonBlockingStatsDClientBuilder;
import com.timgroup.statsd.StatsDClient;
import org.json.JSONObject;

import static example.Context.currentTraceId;
import static example.Context.runtime;

public class Consumer implements RequestHandler<SQSEvent, SQSBatchResponse>{

  private static final StatsDClient statsd = new NonBlockingStatsDClientBuilder().hostname("localhost").build();

  @Override
  public SQSBatchResponse handleRequest(SQSEvent event, Context context)
  {
    String traceId = currentTraceId();
    for (SQSEvent.SQSMessage message : event.getRecords()) {
      JSONObject body = new JSONObject(message.getBody());
      JSONObject msg = new JSONObject(body.optString("Message"));
      System.out.println("received sqs message " + msg);

      statsd.recordDistributionValue("trace_context.propagated.sns-sqs", 1, new String[]{
        "consumer_runtime:" + runtime,
        "producer_runtime:" + msg.optString("runtime"),
        msg.optString("trace_id").equals(traceId) ? "success:true" : "success:false",
        "transport:sns-sqs",
      });
    }
    return new SQSBatchResponse();
  }
}
