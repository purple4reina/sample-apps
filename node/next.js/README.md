This is a starter template for [Learn Next.js](https://nextjs.org/learn).

## Recreating app

1. Create app with `npx create-next-app@latest next.js --use-npm --example
   "https://github.com/vercel/next-learn/tree/master/basics/learn-starter"`

2. Install dependencies with `npm install`

3. Install special next.js version with `npm install /path/to/next-0.0.0.tgz`

4. Create configuration file called `next.config.js` with:

    ```js
    module.exports = {
      experimental: {
        trace: {
          serviceName: 'rey-node-next'
        },
      },
    }
    ```

5. Install datadog-agent running locally, with configuration enabling otlp:

    ```yaml
    otlp_config:
      receiver:
        protocols:
          grpc:
            endpoint: 0.0.0.0:4317
          http:
            endpoint: 0.0.0.0:4318
    ```

6. Run dev server with `npm run dev`

7. View traces in Datadog!

## Installing local Next.js version

Using https://github.com/kwonoj/next.js/pull/7

```bash
$ cd path/to/next/repo
$ pnpm install && pnpm build
$ cd packages/next
$ npm pack
$ cd -
$ npm install path/to/next/tgz/file
```

Run the server with `npm run dev`.

## Grabbing raw trace

1. Create a dummy json file with `touch export.json`
2. Start otel collector with `docker run -v
   $(pwd)/config.yaml:/etc/otelcol/config.yaml -v
   $(pwd)/export.json:/tmp/export.json -p 4318:4318
   otel/opentelemetry-collector:0.70.0`
3. Start node server with `npm run dev`
4. Send traffic to website with `curl http://localhost:3000`
5. Trace should now be exported to the file `export.json`
