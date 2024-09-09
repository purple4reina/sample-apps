package main

import (
	"github.com/DataDog/datadog-cdk-constructs-go/ddcdkconstruct"
	"github.com/aws/aws-cdk-go/awscdk/v2"
	"github.com/aws/jsii-runtime-go"
)

func main() {
	app := awscdk.NewApp(nil)
	stack := awscdk.NewStack(app, jsii.String("Datadog"), &awscdk.StackProps{})
	ddcdkconstruct.NewDatadog(
		stack,
		jsii.String("Datadog"),
		&ddcdkconstruct.DatadogProps{},
	)
	//datadog.AddLambdaFunctions(&[]interface{}{myFunction}, nil)
	//datadog.AddForwarderToNonLambdaLogGroups()
}
