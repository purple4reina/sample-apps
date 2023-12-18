# Local Testing

Demonstrates the ability to run container images locally for testing.

1. Build docker image

  ```
  $ docker build -t localtest .
  ```

2. Run docker container

  ```
  $ docker run -it --rm -p 9000:8080 localtest
  ```

3. Execute function

  ```
  $ curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'
  ```

  Optionally replace the `'{}'` with an event payload, like `'{"hello":"world"}'`
