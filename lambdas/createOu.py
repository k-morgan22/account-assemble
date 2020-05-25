import json
import boto3
from uuid import uuid4

ssm = boto3.client('ssm')
org = boto3.client('organizations')


def grabMasterId():
  
  listRoots = org.list_roots()
  
  return listRoots['Roots'][0]['Id']


def createOrgUnit(rootId, ouName):

  ouResponse = org.create_organizational_unit(
    ParentId = rootId,
    Name = ouName
  )
  
  return ouResponse['OrganizationalUnit']['Id']

# pre-handler global
masterId = grabMasterId()

def lambda_handler(event, context):

  masterName = '/account-assemble/orgIds/master-'+ str(uuid4())
  
  putParameter = ssm.put_parameter(
    Name = masterName,
    Description = 'Master Org Id',
    Value = masterId,
    Type = 'String'
  )

  workloadsId = createOrgUnit(masterId, "Workloads")
  
  workloadsName = '/account-assemble/orgIds/workloads-'+ str(uuid4())
  
  putParameter = ssm.put_parameter(
    Name = workloadsName,
    Description = 'Workloads Ou Id',
    Value = workloadsId,
    Type = 'String'
  )