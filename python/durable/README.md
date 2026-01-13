# Lambda Durable Functions

## Deploy

```bash
$ aweserv cdk deploy
```

## Invoke

```bash
$ aweserv aws lambda invoke \
    --function-name='arn:aws:lambda:us-east-1:425362996713:function:rey-durable-function:$LATEST' \
    --payload=$(echo '{"hello":"world"}' | base64) \
    outfile.txt
```

Then cat the outfile.txt to see what was returned.
