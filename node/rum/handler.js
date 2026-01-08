exports.client = async function(event, context) {
  return {
    statusCode: 200,
    headers: {
      "Content-Type": "text/html",
    },
    body: `
      <!DOCTYPE html>
      <html lang="en">
      <head>
        <script
            src="https://www.datadoghq-browser-agent.com/us1/v6/datadog-rum.js"
            type="text/javascript">
        </script>
        <script>
          window.DD_RUM && window.DD_RUM.init({
            clientToken: "pubaa4717e74993750615779e40ee2994f7",
            applicationId: "0291e751-8aee-4a2b-aeae-56f22b26d07d",
            site: "datadoghq.com",
            service: "reyd-rum",
            env: "rey",
            version: "1.0.0",
            sessionSampleRate: 100,
            sessionReplaySampleRate: 0,
            trackBfcacheViews: true,
            defaultPrivacyLevel: "allow",
            allowedTracingUrls: ["${process.env.SERVER_URL}"],
            trackResources: true,
            trackLongTasks: true,
            trackUserInteractions: true,
          });
        </script>
        <style>
          #responses {
            display: flex;
            flex-direction: column;
            gap: 10px;
            margin: 20px;
          }
          .response {
            border: 1px solid black;
            padding: 10px;
            margin-bottom: 10px;
          }
        </style>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Client Page</title>
      </head>
      <body>
        <div id="responses"></div>
      </body>
      <script>
        document.addEventListener("DOMContentLoaded", async () => {
          const responsesDiv = document.getElementById("responses");
          while (true) {
            const resp = await fetch("${process.env.SERVER_URL}");
            const respJson = await resp.json();
            const pre = document.createElement("pre");
            pre.className = "response";
            pre.textContent = JSON.stringify(respJson, null, 2);
            responsesDiv.appendChild(pre);
            await new Promise(resolve => setTimeout(resolve, 5000));
          }
        });
      </script>
      </html>
    `,
  };
}

exports.server = async function(event, context) {
  return {
    statusCode: 200,
    headers: {
      "Content-Type": "application/json",
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Headers": "*",
    },
    body: JSON.stringify({ event, context }),
  };
}
