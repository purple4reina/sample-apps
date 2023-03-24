# Proxy Extension

A proxy layer that prints all data payloads sent to the backend before
rerouting them.

NOTE: for some reason this proxy is not actually echoing the request bodies,
though it does seem to be working otherwise!

## Usage

Add this to your `serverless.yml`:

```yml
provider:
  layers:
    - { Ref: ProxyExtensionLambdaLayer }
  environment:
    DD_PROXY_HTTP: http://127.0.0.1:3333
    DD_PROXY_HTTPS: http://127.0.0.1:3333

layers:
  proxyExtension:
    package:
      artifact: ../../utils/proxy/ext.zip
```

## Development

If the code for this proxy changes, you will need to build it with: `./build_proxy.sh`
