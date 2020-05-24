from crhelper import CfnResource
import boto3
import json

helper = CfnResource()
ebridge = boto3.client('events')


@helper.create
def create(event, context):
  metadata = {
    "metadata": {
      "service": "assembler-producer",
      "status": "SUCCEEDED"
    }
  }
  response = ebridge.put_events(
    Entries = [
      {
        'Source': 'assembler-producer',
        'DetailType': 'account-assemble event',
        'Detail': json.dumps(metadata) 
      }
    ]
  )


@helper.update
@helper.delete
def no_op(_, __):
    pass


def handler(event, context):
    helper(event, context)