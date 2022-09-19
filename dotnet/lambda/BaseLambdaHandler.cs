using Amazon.Lambda.APIGatewayEvents;
using Amazon.Lambda.Core;
using Amazon.Lambda.Serialization.SystemTextJson;
using System.Net;

namespace MyFunction
{
    public abstract class BaseLambdaHandler
    {
        private APIGatewayHttpApiV2ProxyResponse doIt(string functionName)
        {
            LambdaLogger.Log($"Debug 🌈 {functionName} executing");
            return new APIGatewayHttpApiV2ProxyResponse
            {
                StatusCode = (int)HttpStatusCode.OK,
                Headers = new Dictionary<string, string> { ["Content-Type"] = "text/plain" },
                Body = "hello world!",
            };
        }

        public async Task<APIGatewayHttpApiV2ProxyResponse> InheritedHandlerNotInChildClass(APIGatewayHttpApiV2ProxyRequest input, ILambdaContext context)
        { return this.doIt("InheritedHandlerNotInChildClass"); }

        public async Task<APIGatewayHttpApiV2ProxyResponse> InheritedHandlerInChildClass(APIGatewayHttpApiV2ProxyRequest input, ILambdaContext context)
        { return this.doIt("InheritedHandlerInChildClass"); }
    }
}
