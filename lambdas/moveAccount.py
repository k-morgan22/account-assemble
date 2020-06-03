import boto3
import logging
import os

ssm = boto3.client('ssm')
org = boto3.client('organizations')

#initialize logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def getOrgIds(path, decryption):
  response = ssm.get_parameters_by_path(
    Path = path,
    Recursive = True,
    WithDecryption = decryption
  )
  
  for param in response['Parameters']:
    if 'master' in param['Name']:
      master = param['Value']
    elif 'workloads' in param['Name']:
      workloads = param['Value']
  return master, workloads

[masterId, workloadsId] = getOrgIds('/account-assemble/orgIds', False)

def grabEmail(accountId):
  response = org.describe_account(
    AccountId = accountId
  )

  email = response['Account']['Email']
  return email


def moveAccount(newAccountId, rootId, destinationId):

  moveResponse = org.move_account(
    AccountId = newAccountId,
    SourceParentId = rootId,
    DestinationParentId = destinationId
  )

def lambda_handler(event, context):
  accountId = event['accountId']
  accountEmail = grabEmail(accountId)
  accountParameter = os.environ['accountEmail']

  if accountEmail == accountParameter:
    moveAccount(accountId, masterId, workloadsId)
  else:
    logger.info("Accidental Trigger")