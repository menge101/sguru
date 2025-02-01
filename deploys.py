from aws_cdk import (
    Stage,
)
from constructs import Construct
from infrastructure import simple


class Development(Stage):
    def __init__(self, scope: Construct, id_: str, **kwargs):
        super().__init__(scope, id_, **kwargs)
        simple.SimpleStack(
            self,
            "dev",
        )
