AWS Lambda Test Environment
---------------------------

This repository provides a way to automatically create a lambda using terraform in the newrelic-ee environment.

Instructions
------------

Using this module requires installing [oktaws](https://source.datanerd.us/cloud-core/oktaws) and [terraform](https://www.terraform.io/)

To install terraform:
```bash
brew install terraform
```

Variables
----------

| Variable Name | Purpose                                                            | Default       |
| ---           | ---                                                                | ---           |
| runtime       | Define the lambda runtime for execution of the serverless function | python3.6     |
| function_name | Namespace for lambda functions to execute                          | agent-testing |
| handler       | Path to the lambda function entrypoint                             | main.handler  |

Usage
-----

Log into aws using oktaws and set `AWS_PROFILE` in your environment.

```
$ export AWS_PROFILE=pdx_datacenter/okta_pythonagentteam
```

For the initial setup, run the following and follow instructions:

```bash
terraform init
terraform apply
```

On subsequent runs (after updating the source)

```bash
terraform apply
```

FAQ
----

* Q: It doesn't work. When I run terraform apply I get a permission denied error. Why?
* A: The most common issue I've seen here is that you have `AWS_ACCESS_KEY` and `AWS_SECRET_KEY` set as environment variables in your shell. These environment variables override the `oktaws` configuration. In order to proceed, you should unset both of those environment variables and try again.
