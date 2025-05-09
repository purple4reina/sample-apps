import os

from aws_cdk import (
        Stack,
        aws_ec2 as ec2,
        aws_ecs as ecs,
        aws_apigatewayv2 as apigwv2,
        aws_apigatewayv2_integrations as apigwv2_integrations,
        aws_ecs_patterns as ecs_patterns,
        aws_logs as logs,
)

class EcsFargateStack(Stack):

    dd_api_key = os.environ["DD_API_KEY"]

    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # fargate
        vpc = ec2.Vpc(self, "ReyVpc", max_azs=3)     # default is all AZs in region
        cluster = ecs.Cluster(self, "ReyCluster", vpc=vpc)
        fargate = ecs.FargateService(
            self, "ReyFargateService",
            cluster=cluster,
            task_definition=ecs.FargateTaskDefinition(self, "ReyTaskDef"),
        )

        # datadog agent container
        datadog_agent_container = fargate.task_definition.add_container(
            "datadog-agent",
            image=ecs.ContainerImage.from_registry("public.ecr.aws/datadog/agent:latest"),
            environment={
                "DD_API_KEY": self.dd_api_key,
                "DD_APM_ENABLED": "true",
                "ECS_FARGATE": "true",
            },
            port_mappings=[{
                "containerPort": 8126,
                "protocol": ecs.Protocol.TCP,
            }],
        )

        # webapp container
        webapp = fargate.task_definition.add_container(
            "ReyWebApp",
            image=ecs.ContainerImage.from_asset("."),
            environment={
                "DD_API_KEY": self.dd_api_key,
                "DD_APM_ENABLED": "true",
                "DD_SERVICE": "rey-ecs-fargate",
            },
            port_mappings=[{
                "containerPort": 80,
                "protocol": ecs.Protocol.TCP,
            }],
            logging=ecs.LogDrivers.aws_logs(
                stream_prefix="rey-webapp",
                log_group=logs.LogGroup(
                    self, "ReyWebAppLogGroup",
                    retention=logs.RetentionDays.ONE_DAY,
                    log_group_name="/rey-webapp"
                ),
            ),
        )

        # api gateway
        api = apigwv2.HttpApi(self, "ReyHttpApi")
        alb = ecs_patterns.ApplicationLoadBalancedFargateService(
            self, "ReyAlbFargateService",
            cluster=cluster,
            task_definition=fargate.task_definition,
            public_load_balancer=True,
        )
        api.add_routes(
            path="/{proxy+}",
            methods=[apigwv2.HttpMethod.ANY],
            integration=apigwv2_integrations.HttpAlbIntegration(
                "ReyIntegration",
                listener=alb.listener,
                method=apigwv2.HttpMethod.ANY,
                vpc_link=apigwv2.VpcLink(self, "ReyVpcLink", vpc=vpc),
            ),
        )
