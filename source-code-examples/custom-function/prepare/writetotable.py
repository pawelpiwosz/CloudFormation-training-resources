"""Custom Lambda function"""

import json
import logging
import boto3
import datetime
from botocore.vendored import requests


currenttime = datetime.datetime.now()
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#  Copyright 2016 Amazon Web Services, Inc. or its affiliates. All Rights Reserved.
#  This file is licensed to you under the AWS Customer Agreement (the "License").
#  You may not use this file except in compliance with the License.
#  A copy of the License is located at http://aws.amazon.com/agreement/ .
#  This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, express or implied.
#  See the License for the specific language governing permissions and limitations under the License.
 
#from botocore.vendored import requests
#import json
 
SUCCESS = "SUCCESS"
FAILED = "FAILED"
 
def send(event, context, responseStatus, responseData, physicalResourceId=None, noEcho=False):
    responseUrl = event['ResponseURL']
 
    print(responseUrl)
 
    responseBody = {}
    responseBody['Status'] = responseStatus
    responseBody['Reason'] = 'See the details in CloudWatch Log Stream: ' + context.log_stream_name
    responseBody['PhysicalResourceId'] = physicalResourceId or context.log_stream_name
    responseBody['StackId'] = event['StackId']
    responseBody['RequestId'] = event['RequestId']
    responseBody['LogicalResourceId'] = event['LogicalResourceId']
    responseBody['NoEcho'] = noEcho
    responseBody['Data'] = responseData
 
    json_responseBody = json.dumps(responseBody)
 
    print("Response body:\n" + json_responseBody)
 
    headers = {
        'content-type' : '',
        'content-length' : str(len(json_responseBody))
    }
 
    try:
        response = requests.put(responseUrl,
                                data=json_responseBody,
                                headers=headers)
        print("Status code: " + response.reason)
    except Exception as e:
        print("send(..) failed executing requests.put(..): " + str(e))

def write2dynamo(event, context):
    messagevalue = ''
    dynamodb_resource = boto3.resource('dynamodb')
    dynamodb_client = boto3.client('dynamodb')
    data_table = dynamodb_resource.Table('TrainingTable')
    logger.info('REQUEST RECEIVED:\n %s', event)
    logger.info('REQUEST RECEIVED:\n %s', context)
    if event['RequestType'] == 'Create':
        logger.info('CREATE!')
        messagevalue = 'Create stack'
    elif event['RequestType'] == 'Update':
        logger.info('UPDATE!')
        messagevalue = 'Update stack'
    elif event['RequestType'] == 'Delete':
        logger.info('DELETE!')
        messagevalue = 'Delete stack'
    else:
        logger.info('FAILED!')
        messagevalue = 'Operation on stack failed'
    try:
        data_table.put_item(
            Item={
                'Element': messagevalue,
                'ElementValue': currenttime.isoformat()
            }
        )
    except dynamodb_client.exceptions.ClientError as error:
        logger.info('Something wrong during write!')
        responseData = {}
        responseData['Data'] = error
        send(event, context, FAILED, responseData, "CustomResourcePhysicalID")
    responseData = {}
    responseData['Data'] = 'Goood!'
    send(event, context, SUCCESS, responseData, "CustomResourcePhysicalID")
