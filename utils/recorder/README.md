# Recorder Extension

A layer that prints all data payloads intended to be sent to the backend.

## Usage

Add this to your `serverless.yml`:

```yml
provider:
  layers:
    - { Ref: RecorderExtensionLambdaLayer }

layers:
  recorderExtension:
    package:
      artifact: ../../utils/recorder/recorder-extension/ext.zip
```

## Development

If the code for this recorder changes, you will need to build it with: `./build_recorder.sh`
