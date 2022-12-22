using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using System.Net;

// Assembly attribute to enable the Lambda function's JSON input to be converted into a .NET class.
[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace MyFunction;

public class Function
{
    static readonly HttpClient client = new HttpClient();

    public string Handler(APIGatewayProxyRequest request, ILambdaContext context)
    {
        var task = Task.Run(() => client.GetStringAsync("https://example.com"));
        task.Wait();
        return task.Result;
    }
}
