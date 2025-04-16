import os

from aws_cdk import (
        Stack,
        aws_ec2 as ec2,
        aws_ecs as ecs,
        aws_ecs_patterns as ecs_patterns,
)

class EcsFargateStack(Stack):

    dd_api_key = os.environ["DD_API_KEY"]

    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        # cluster
        vpc = ec2.Vpc(self, "ReyVpc", max_azs=3)     # default is all AZs in region
        cluster = ecs.Cluster(self, "ReyCluster", vpc=vpc)

        # app container
        alb = ecs_patterns.ApplicationLoadBalancedFargateService(
                self, "ReyFargateService",
                cluster=cluster,
                task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(
                    image=ecs.ContainerImage.from_asset("."),
                    environment={
                        "DD_API_KEY": self.dd_api_key,
                        "DD_APM_ENABLED": "true",
                        "DD_SERVICE": "rey-ecs-fargate",
                    },
                ),
        )

        # datadog agent container
        datadog_agent_container = alb.task_definition.add_container(
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
