# .NET Lambda function

1. Add the templates

    ```bash
    $ dotnet new -i Amazon.Lambda.Templates
    ```

2. Install tools

    ```bash
    $ dotnet tool install -g Amazon.Lambda.Tools
    ```

    Or update them

    ```bash
    $ dotnet tool update -g Amazon.Lambda.Tools
    ```

3. Build the zip

    ```bash
    $ dotnet lambda package --configuration Release --output-package ./handler.zip
    ```
