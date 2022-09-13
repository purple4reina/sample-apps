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

    public struct MyInputType
    {
        public MyInputType(string key1, string key2, string key3)
        {
            Key1 = key1;
            Key2 = key2;
            Key3 = key3;
        }

        public string Key1 { get; set; }
        public string Key2 { get; set; }
        public string Key3 { get; set; }

        public override string ToString() => $"({Key1}, {Key2}, {Key3})";
    }

    private string handle(string functionName)
    {
        LambdaLogger.Log($"Debug 🌈 {functionName} executing");
        using (var scope = Tracer.Instance.StartActive($"my-span-{functionName}"))
        {
            scope.Span.SetTag("context", functionName);

            var task = Task.Run(() => client.GetStringAsync("https://example.com"));
            task.Wait();
            var responseBody = task.Result;
        }
        return "Hello World!";
    }

    // ASYNC HANDLERS, RETURN STRING

    public async Task<string> HandlerDictParam(Dictionary < string, string > input, ILambdaContext context)
    { return this.handle("HandlerDictParam"); }

    public async Task<string> HandlerStringParam(string input, ILambdaContext context)
    { return this.handle("HandlerStringParam"); }

    public async Task<string> HandlerAPIGatewayParam(APIGatewayProxyRequest request, ILambdaContext context)
    { return this.handle("HandlerAPIGatewayParam"); }

    public async Task<string> HandlerNoParam()
    { return this.handle("HandlerNoParam"); }

    public async Task<string> HandlerCustomStructParam(MyInputType input, ILambdaContext context)
    { return this.handle("HandlerCustomStructParam"); }

    // ASYNC HANDLERS, RETURN VOID

    public async Task HandlerDictParamVoid(Dictionary < string, string > input, ILambdaContext context)
    { this.handle("HandlerDictParamVoid"); }

    public async Task HandlerStringParamVoid(string input, ILambdaContext context)
    { this.handle("HandlerStringParamVoid"); }

    public async Task HandlerAPIGatewayParamVoid(APIGatewayProxyRequest request, ILambdaContext context)
    { this.handle("HandlerAPIGatewayParamVoid"); }

    public async Task HandlerNoParamVoid()
    { this.handle("HandlerNoParamVoid"); }

    public async Task HandlerCustomStructParamVoid(MyInputType input, ILambdaContext context)
    { this.handle("HandlerCustomStructParamVoid"); }

    // NON-ASYNC HANDLERS, RETURN STRING

    public string HandlerDictParamSync(Dictionary < string, string > input, ILambdaContext context)
    { return this.handle("HandlerDictParamSync"); }

    public string HandlerStringParamSync(string input, ILambdaContext context)
    { return this.handle("HandlerStringParamSync"); }

    public string HandlerAPIGatewayParamSync(APIGatewayProxyRequest request, ILambdaContext context)
    { return this.handle("HandlerAPIGatewayParamSync"); }

    public string HandlerNoParamSync()
    { return this.handle("HandlerNoParamSync"); }

    public string HandlerCustomStructParamSync(MyInputType input, ILambdaContext context)
    { return this.handle("HandlerCustomStructParamSync"); }

    // NON-ASYNC HANDLERS, RETURN VOID

    public void HandlerDictParamSyncVoid(Dictionary < string, string > input, ILambdaContext context)
    { this.handle("HandlerDictParamSyncVoid"); }

    public void HandlerStringParamSyncVoid(string input, ILambdaContext context)
    { this.handle("HandlerStringParamSyncVoid"); }

    public void HandlerAPIGatewayParamSyncVoid(APIGatewayProxyRequest request, ILambdaContext context)
    { this.handle("HandlerAPIGatewayParamSyncVoid"); }

    public void HandlerNoParamSyncVoid()
    { this.handle("HandlerNoParamSyncVoid"); }

    public void HandlerCustomStructParamSyncVoid(MyInputType input, ILambdaContext context)
    { this.handle("HandlerCustomStructParamSyncVoid"); }
}
