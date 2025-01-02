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

    public string Handler(APIGatewayProxyRequest request, ILambdaContext context)
    {
        using (var scopeOuter = Tracer.Instance.StartActive("rey.http.request.outer"))
        {
            using (var scopeInner = Tracer.Instance.StartActive("rey.http.request.inner"))
            {
                var response = client.GetAsync("https://example.com").Result;
                response.EnsureSuccessStatusCode();
                return response.Content.ReadAsStringAsync().Result;
            }
        }
    }
}
