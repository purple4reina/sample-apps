# Rust Lambda

1. Install
    ```bash
    $ brew tap cargo-lambda/cargo-lambda
    $ brew install cargo-lambda
    ```

2. Create
    ```bash
    $ cargo lambda new YOUR_FUNCTION_NAME
    ```

3. Build
    ```bash
    $ cargo lambda build --release
    ```

4. Deploy
    ```bash
    $ aweserv cargo lambda deploy --region sa-east-1
    ```
    or
    ```bash
    $ aweserv sls deploy
    ```
