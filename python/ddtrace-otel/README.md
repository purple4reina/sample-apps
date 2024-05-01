# ddtrace + opentelemetry

## Running locally

1. Add env vars
  ```
  DD_TRACE_OTEL_ENABLED=true
  DD_SERVICE=rey-ddtrace-otel
  DD_ENV=rey
  ```

2. Configure otel trace provider
  a. On commandline
      ```bash
      $ ddtrace-run python app.py
      ```
  b. In code
      ```python
      from opentelemetry.trace import set_tracer_provider
      from ddtrace.opentelemetry import TracerProvider

      set_tracer_provider(TracerProvider())
      ```

3. Instrument code
  a. Using opentelemetry
      ```python
      import opentelemetry.trace
      tracer = opentelemetry.trace.get_tracer(__name__)

      with tracer.start_as_current_span("ddtrace-otel-span") as span:
          span.set_attribute("key", "value")
      ```
  b. Using ddtrace
      ```python
      from ddtrace import tracer

      with tracer.trace("ddtrace-otel-span") as span:
          span.set_tag("key", "value")
      ```

4. Run
    ```bash
    $ ./run.sh
    ```

## Running in Lambda
