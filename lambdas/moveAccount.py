import boto3
import logging

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

def grabName(accountId):
  response = org.describe_account(
    AccountId = accountId
  )

  name = response['Account']['Name']
  return name


def moveAccount(newAccountId, rootId, destinationId):

  moveResponse = org.move_account(
    AccountId = newAccountId,
    SourceParentId = rootId,
    DestinationParentId = destinationId
  )

def lambda_handler(event, context):
  accountId = event['accountId']
  accountName = grabName(accountId)

  if accountName in ["Dev", "Staging", "Prod"]:
    moveAccount(accountId, masterId, workloadsId)
    message = "accountName: " + accountName + ", accountId: " + accountId

    return message
  else:
    logger.info("Accidental Trigger")