# Use the lambda basic execution role
# This role adds basic execution permissions and write access to cloud watch
data "aws_iam_role" "lambda_basic" {
    name = "lambda_basic_execution"
}
