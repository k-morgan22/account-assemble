import json
import requests
import boto3

secret = boto3.client('secretsmanager')


def getUrl():
  urlResponse = secret.get_secret_value(
    SecretId = '/account-assemble/slack/slackUrl'
  )
  url = urlResponse['SecretString']
  return url

slackUrl = getUrl()

def lambda_handler(event, context):

  message = json.dumps(event) 

  slackResponse = requests.post(
    slackUrl,
    json = {"text": message},
    headers = {'Content-Type': 'application/json'}
  )

  http_reply = {
    "statusCode": slackResponse.status_code,
    "body": slackResponse.text
  }

  return http_reply