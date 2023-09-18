package example;

import io.opentracing.util.GlobalTracer;
import io.opentracing.Tracer;
import io.opentracing.SpanContext;

public class Context {

  private static Tracer tracer = GlobalTracer.get();
  public static final String runtime = System.getenv("AWS_EXECUTION_ENV").replace("AWS_Lambda_", "");

  public static String currentTraceId() {
    SpanContext ctx = tracer.activeSpan().context();
    System.out.println("found trace context: traceId=" + ctx.toTraceId() + " spanId=" + ctx.toSpanId());
    return ctx.toTraceId();
  }
}
