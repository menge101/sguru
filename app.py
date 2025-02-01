import aws_cdk as cdk
import deploys

app = cdk.App()
deploys.Development(app, "development")
app.synth()
