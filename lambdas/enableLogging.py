import json
import boto3
import os

org = boto3.client('organizations')
trail = boto3.client('cloudtrail')

def getAccountId(accountEmail):
  response = org.list_accounts()
  for account in response['Accounts']:
    if (account['Email'] == accountEmail):
      accountId = account['Id']
  
  return accountId

def isOrg():
  orgEnabled = False
  response = trail.describe_trails(
    includeShadowTrails = False
  )
  cloudtrail = response['trailList'][0]
  if cloudtrail['IsOrganizationTrail'] == True:
    orgEnabled = True
  trailName = cloudtrail['Name']
  
  return orgEnabled, trailName

def updateTrail(trailName):
  response = trail.update_trail(
    Name = trailName,
    IsOrganizationTrail = True
  )


def addEvent(trailName, bucket):
  response = trail.put_event_selectors(
    TrailName = trailName,
    EventSelectors = [
      {
        'DataResources': [
          {
            'Type': 'AWS::S3::Object',
            'Values': [
              bucket
            ]
          }
        ]
      }
    ]
  )

def lambda_handler(event, context):
  accountEmail = os.environ['accountEmail']

  orgEnabled, trailName = isOrg()

  if(orgEnabled != True):
    updateTrail(trailName)

  accountId = getAccountId(accountEmail)
  accountBucket = f"arn:aws:s3:::bucket-{accountId}/" 
  
  addEvent(trailName, accountBucket)
