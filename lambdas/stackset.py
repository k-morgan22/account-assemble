import json
import boto3
from uuid import uuid4
import time
import logging

ssm = boto3.client('ssm')
cf = boto3.client('cloudformation')
ebridge = boto3.client('events')

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def getOuIds(path, decryption):
  response = ssm.get_parameters_by_path(
    Path = path,
    Recursive = True,
    WithDecryption = decryption
  )
  
  for param in response['Parameters']:
    if 'workloads' in param['Name']:
      workloads = param['Value']
  return workloads

#pre-handler global var
workloadsId = getOuIds('/account-assemble/orgIds', False)

def createBaseStack():
  try:
    baselineStackName = "account-baseline-" + str(uuid4())  
  
    baselineStackResponse = cf.create_stack_set(
      StackSetName = baselineStackName,
      Description = 'Baseline for new accounts',
      TemplateURL='https://testing-org-lambda.s3.amazonaws.com/accountAssembleBase.yml',
      Capabilities= [
        'CAPABILITY_NAMED_IAM'
      ],
      PermissionModel='SERVICE_MANAGED',
      AutoDeployment={
        'Enabled': True,
        'RetainStacksOnAccountRemoval': False
      }
    )
    
    return baselineStackName
  except Exception as e:
    logger.error(e)
    raise
  
  


def deployBaselineStack(stackName, ou):
  try:
    deployBaseResponse = cf.create_stack_instances(
      StackSetName=stackName,
      DeploymentTargets={
        'OrganizationalUnitIds': [
          ou
        ]
      },
      Regions=[
        'us-east-1'
      ],
      OperationPreferences={
        'FailureTolerancePercentage': 0,
        'MaxConcurrentPercentage': 100
      }
    )
    
    baselineOpId = deployBaseResponse['OperationId']
    
    while True:
      deployBaseStatus = cf.describe_stack_set_operation(
        StackSetName=stackName,
        OperationId=baselineOpId
      )
      if deployBaseStatus['StackSetOperation']['Status'] == 'RUNNING':
        time.sleep(10)
      elif deployBaseStatus['StackSetOperation']['Status'] == 'SUCCEEDED':
        break
  except Exception as e:
    logger.error(e)
    raise
  

def putEvent():
  metadata = {
    "metadata": {
      "service": "assembler-stackset",
      "status": "SUCCEEDED"
    }
  }
  response = ebridge.put_events(
    Entries = [
      {
        'Source': 'assembler-stackset',
        'DetailType': 'account-assemble event',
        'Detail': json.dumps(metadata) 
      }
    ]
  )

def lambda_handler(event, context):
  if "errorCode" not in event:
    envStackName = createBaseStack()
    deployBaselineStack(envStackName, workloadsId)

    putEvent()
  else:
    logger.info("Triggered by error")
