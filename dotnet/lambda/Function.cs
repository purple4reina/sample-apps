using Amazon.Lambda.Core;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace ReyFunction;

public class Function
{
    public string FunctionHandler(Dictionary < string, string > input, ILambdaContext context)
    {
        LambdaLogger.Log("Hello World!");
        return "Hello World!";
    }
}
