from aws_cdk import (
        Stack,
        aws_ec2 as ec2,
        aws_ecs as ecs,
        aws_ecs_patterns as ecs_patterns,
)

class EcsFargateStack(Stack):

    def __init__(self, scope, construct_id, **kwargs):
        super().__init__(scope, construct_id, **kwargs)

        vpc = ec2.Vpc(self, "ReyVpc", max_azs=3)     # default is all AZs in region
        cluster = ecs.Cluster(self, "ReyCluster", vpc=vpc)
        image = ecs.ContainerImage.from_registry("amazon/amazon-ecs-sample")

        alb = ecs_patterns.ApplicationLoadBalancedFargateService(
                self, "ReyFargateService",
                cluster=cluster,
                task_image_options=ecs_patterns.ApplicationLoadBalancedTaskImageOptions(image=image),
        )
