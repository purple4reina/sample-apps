# Recorder Extension

A layer that prints all data payloads intended to be sent to the backend.

## Usage

Add this to your `serverless.yml`:

```yml
provider:
  layers:
    - { Ref: RecorderExtensionLambdaLayer }
  environment:
    DD_DD_URL: http://127.0.0.1:3333
    DD_LOGS_CONFIG_LOGS_DD_URL: 127.0.0.1:3333  # NOTE THIS ONE IS DIFFERENT
    DD_APM_DD_URL: http://127.0.0.1:3333

layers:
  recorderExtension:
    package:
      artifact: ../../utils/recorder/recorder-extension/ext.zip
```

## Development

If the code for this recorder changes, you will need to build it with: `./build_recorder.sh`
