data "aws_lambda_invocation" "test" {
  function_name = "${aws_lambda_function.lambda.function_name}"
  depends_on = ["aws_lambda_function.lambda"]

  input = <<JSON
{
}
JSON

}

output "result" {
  value = "${data.aws_lambda_invocation.test.result}"
}
