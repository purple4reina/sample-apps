# Boto

This is a directory for apps that use `botocore` and other amazon like things.

## S3

The app in the `s3.py` file currently does not use the python agent at all. It
was created in order to debug an issue with `moto` (mocking package for `boto`
testing) where responses were not getting the `RequestId` metadata key.  This
was happening because `moto` was not including the `x-amz-request-id` header in
_any_ of its responses. The fix is to create a transient function wrapper that
patches all responses and adds the header.

Once instrumentation improvements have been completed for the python agent and
`botocore`, you'll be able to see the `RequestId` captured as an agent
attribute.
