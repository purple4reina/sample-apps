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

    private async Task<string> handle(string functionName)
    {
        LambdaLogger.Log($"Debug 🌈 {functionName} executing");
        using (var scope = Tracer.Instance.StartActive("my-span"))
        {
            scope.Span.SetTag("context", functionName);

            string responseBody = await client.GetStringAsync("https://example.com");
        }
        return "Hello World!";
    }

    // incorrect parenting
    public async Task<string> HandlerDictParam(Dictionary < string, string > input, ILambdaContext context)
    { return await this.handle("HandlerDictParam"); }

    // correct parenting
    public async Task<string> HandlerStringParam(string input, ILambdaContext context)
    { return await this.handle("HandlerStringParam"); }

    // fails
    [LambdaSerializer(typeof(Dictionary < string, string >))]
    public async Task<string> HandlerDictParamWrapped1(Dictionary < string, string > input, ILambdaContext context)
    { return await this.handle("HandlerDictParamWrapped1"); }

    // correct parenting
    public async Task<string> HandlerAPIGatewayParam(APIGatewayProxyRequest request, ILambdaContext context)
    { return await this.handle("HandlerAPIGatewayParam"); }

    // correct parenting
    public async Task<string> HandlerNoParam()
    { return await this.handle("HandlerNoParam"); }

    public struct MyInputType
    {
        public MyInputType(string key1, string key2, string key3)
        {
            Key1 = key1;
            Key2 = key2;
            Key3 = key3;
        }

        public string Key1 { get; }
        public string Key2 { get; }
        public string Key3 { get; }

        public override string ToString() => $"({Key1}, {Key2}, {Key3})";
    }

    // incorrect parenting
    public async Task<string> HandlerCustomStructParam(MyInputType input, ILambdaContext context)
    { return await this.handle("HandlerCustomStructParam"); }

    // TODO: Also test other return types
    // TODO: Also test non-async handlers
}
