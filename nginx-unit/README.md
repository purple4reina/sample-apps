# Nginx Unit

An example of using the agent with Nginx's Unit (which is still in beta). As of
now, there is a bug in their code which causes a `Fatal Python` error
preventing deploy.

1. Build docker image

    ```
    $ docker build -t unit .
    ```

2. Start the container

    ```
    $ docker run -it unit
    ```

3. From another terminal, exec into the container

    ```
    $ docker exec -it $(docker ps -q | head -n1) bash
    ```

4. Load configuration

    ```
    $ service unit loadconfig /usr/share/doc/unit-python2.7/examples/unit.config
    ```

5. Send it traffic

    ```
    $ curl http://localhost:8400/
    ```

6. Watch the crash in the other terminal
