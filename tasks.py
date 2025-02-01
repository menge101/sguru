from invoke import task
import boto3


@task
def send_message_to_topic(_ctx, topic_arn, recipient_id, message, type):
    client = boto3.client("sns")
    response = client.publish(
        TopicArn=topic_arn,
        Message=message,
        MessageAttributes={
            "type": {"DataType": "String", "StringValue": type},
            "recipient_id": {"DataType": "String", "StringValue": recipient_id},
        },
    )
    print(response["MessageId"])
