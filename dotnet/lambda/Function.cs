using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using Datadog.Trace;
using System.Net;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace MyFunction;

public class Function
{
    static readonly HttpClient client = new HttpClient();

    //public async Task<string> FunctionHandler(Dictionary < string, string > input, ILambdaContext context)
    public async Task<string> FunctionHandler(APIGatewayProxyRequest request, ILambdaContext context)
    {
        LambdaLogger.Log("[Debug] FunctionHandler executing");
        using (var scope = Tracer.Instance.StartActive("my-span"))
        {
            scope.Span.SetTag("context", "purple");

            string responseBody = await client.GetStringAsync("https://example.com");
            LambdaLogger.Log(responseBody);
        }
        return "Hello World!";
    }
}
