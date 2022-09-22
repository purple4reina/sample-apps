using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using Datadog.Trace;
using System.Net;
using System.Text.Json;
using System;

[assembly: LambdaSerializer(typeof(Amazon.Lambda.Serialization.SystemTextJson.DefaultLambdaJsonSerializer))]

namespace Function;

public class Function
{
    static readonly HttpClient client = new HttpClient();
    static readonly string baseUrl = Environment.GetEnvironmentVariable("REY_FUNCTION_URL_BASE");

    private string GetURL(string path)
    {
        var url = $"{baseUrl}/{path}";
        LambdaLogger.Log($"Debug 🌈 Getting url: {url}");
        var task = Task.Run(() => client.GetStringAsync(url));
        task.Wait();
        return task.Result;
    }

    public APIGatewayProxyResponse HandlerFunction1(APIGatewayProxyRequest request, ILambdaContext context)
    {
        using (var scope = Tracer.Instance.StartActive($"my-span-function-1"))
        {
            return new APIGatewayProxyResponse
            {
                StatusCode = (int)HttpStatusCode.OK,
                Body = JsonSerializer.Serialize(new Dictionary<string, string>(){
                    {"response_body", this.GetURL("function-2")},
                    {"base_url", baseUrl},
                    {"path", "function-2"},
                })
            };
        }
    }

    public APIGatewayProxyResponse HandlerFunction2(APIGatewayProxyRequest request, ILambdaContext context)
    {
        using (var scope = Tracer.Instance.StartActive($"my-span-function-2"))
        {
            return new APIGatewayProxyResponse
            {
                StatusCode = (int)HttpStatusCode.OK,
                Body = "{\"Hello\": \"World\"}"
            };
        }
    }
}
