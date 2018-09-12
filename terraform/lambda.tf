provider "aws" {
  region     = "us-west-2"
}


# Create source archive to upload to AWS
data "archive_file" "source" {
    type = "zip"
    source_dir = "function"
    output_path = "build/source.zip"
}


# Define the lambda function
data "aws_caller_identity" "current" {}

locals {
    function_name = "${element(split(":", data.aws_caller_identity.current.user_id), 1)}-${var.runtime}-${var.function_name}"
}

resource "aws_lambda_function" "lambda" {
    filename = "${data.archive_file.source.output_path}"
    source_code_hash = "${data.archive_file.source.output_base64sha256}"

    runtime       = "${var.runtime}"
    function_name = "${replace(local.function_name, ".", "")}"
    role          = "${data.aws_iam_role.lambda_basic.arn}"

    handler       = "${var.handler}"

    lifecycle {
        ignore_changes = [
            "filename",
            "last_modified",
        ]
    }
}
