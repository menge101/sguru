from aws_cdk import (
    aws_iam as iam,
    aws_lambda as lam,
    aws_sns as sns,
    aws_sns_subscriptions as subs,
    aws_sqs as sqs,
)
from constructs import Construct
from typing import cast


class Subscribable(Construct):
    def __init__(
        self,
        scope: Construct,
        id_: str,
        subscription_type: str,
    ) -> None:
        super().__init__(scope, id_)
        self.subscription_type = subscription_type
        self.policy = iam.ManagedPolicy(
            self,
            "policy",
            statements=[
                iam.PolicyStatement(
                    actions=["logs:*"],
                    effect=iam.Effect.ALLOW,
                    resources=["arn:aws:logs:*"],
                )
            ],
        )
        self.role = iam.Role(
            self,
            "role",
            assumed_by=iam.ServicePrincipal("lambda.amazonaws.com"),
            managed_policies=[self.policy],
        )
        self.function = lam.Function(
            self,
            "logging",
            code=lam.Code.from_asset("./build/logging.zip"),
            handler="lib.logging.handler",
            runtime=cast(lam.Runtime, lam.Runtime.PYTHON_3_13),
            role=self.role,
        )
        self.dlq = sqs.Queue(
            self, "dlq-q", enforce_ssl=True, encryption=sqs.QueueEncryption.SQS_MANAGED
        )

    def generate_subscription(self) -> sns.ITopicSubscription:
        return subs.LambdaSubscription(
            fn=self.function,
            dead_letter_queue=self.dlq,
            filter_policy={
                "type": sns.SubscriptionFilter.string_filter(
                    allowlist=[self.subscription_type]
                )
            },
        )
