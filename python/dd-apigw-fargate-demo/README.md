# ecs-fargate

Used to test changes to datadog-cdk-constructs for API Gateway inferred spans
support.

To install testing version of datadog-cdk-constructs from local changes:

1. from datadog-cdk-constructs repo

  ```bash
  $ npx projen compile
  $ rm -rf node_modules
  $ npm pack
  ```

2. from cdk directory here

  ```bash
  $ npm install /Users/rey.abolofia/dd/datadog-cdk-constructs/datadog-cdk-constructs-v2-0.0.0.tgz
  ```
