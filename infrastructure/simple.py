from aws_cdk import (
    aws_kms as kms,
    aws_iam as iam,
    aws_sns as sns,
    RemovalPolicy,
    Stack,
)
from constructs import Construct
from infrastructure.subscribable import Subscribable


class Simple(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        removal_policy: RemovalPolicy = RemovalPolicy.RETAIN,
    ):
        super().__init__(scope, id_)
        key = kms.Key(
            self,
            "Key",
            description="Key to be used in the simple notification system",
            removal_policy=removal_policy,
            enable_key_rotation=True,
        )
        self.topic = sns.Topic(self, "notify", enforce_ssl=True, master_key=key)


class SimpleStack(Stack):
    def __init__(self, scope: Construct, id_: str):
        super().__init__(scope, id_)
        sms_service = Subscribable(self, "SMSService", "sms")
        email_service = Subscribable(self, "EmailService", "email")
        push_service = Subscribable(self, "PushService", "push")
        notification_service = Simple(
            self, "NotificationService", removal_policy=RemovalPolicy.DESTROY
        )
        notification_service.topic.add_subscription(sms_service.generate_subscription())
        notification_service.topic.add_subscription(
            email_service.generate_subscription()
        )
        notification_service.topic.add_subscription(
            push_service.generate_subscription()
        )
        queue_policy = iam.PolicyStatement(
            actions=["sqs:SendMessage"],
            effect=iam.Effect.ALLOW,
            principals=[iam.ServicePrincipal("sns.amazonaws.com")],
        )
        sms_service.dlq.add_to_resource_policy(queue_policy)
        email_service.dlq.add_to_resource_policy(queue_policy)
        push_service.dlq.add_to_resource_policy(queue_policy)
