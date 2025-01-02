# Custom Spans with Dotnet Functions

Make sure that the compiled version of the function does not include the tracer
dll file.  You must ensure that there is just one tracer package installed, and
it is the one from the layer.

1. In your `.csproj` file, make sure the tracer version the project is built
   with matches the tracer version installed in the tracing layer. See Datadog
   Lambda tracing layer for .NET [release
   notes](https://github.com/DataDog/dd-trace-dotnet-aws-lambda-layer/releases)
   to determine which version of the Datadog tracer is packaged with your layer
   version.

2. Compile your Lambda function as normal.

3. Locate the packaged zip file. The Datadog tracer dll file must be removed.
   To do so, unzip, remove the tracer, and re-zip the package. The Datadog
   tracer file will be named something like `Datadog.Trace.dll`.

    ```bash
    $ zip -d .package/handler.zip Datadog.Trace.dll
    ```

    Note, this is already done as part of the `./build_deploy.sh` script.

4. Deploy your code as normal.
