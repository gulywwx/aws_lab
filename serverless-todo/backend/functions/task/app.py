import decimal
import json
import logging
import os
import uuid

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['TASK_TABLE'])


def lambda_handler(event, context):
	logger.info('## EVENT\r' + json.dumps(event, indent=2))

	if event['httpMethod'] == 'GET':
		if 'pathParameters' not in event or event['pathParameters'] == None:
			response = getTasks()
			return createResponse(json.dumps(response, indent=2, default=handle_decimal_type),200)
		else:
			if 'id' not in event['pathParameters']:
				return createResponse(json.dumps({'msg': 'Bad Request'}),400)
			id = event['pathParameters']['id']
			response = getTask(id)
			if ('Item' not in response):
				return createResponse(json.dumps({'msg': 'Task not found'}),404)
			return createResponse(json.dumps(response['Item'], indent=2, default=handle_decimal_type),200)

	elif event['httpMethod'] == 'POST':
		if ('body' not in event or event['body'] == None or 'title' not in event['body']):
			return createResponse(json.dumps({'msg': 'Bad Request'}),400)

		task = json.loads(event["body"])
		response = 	createTask(task)
		return createResponse(json.dumps({'msg': 'A new task was saved successfully in database'}),200)

	elif event['httpMethod'] == 'PUT':
		if ('body' not in event or event['body'] == None or 'title' not in event['body'] or  'id' not in event['body']):
			return createResponse(json.dumps({'msg': 'Bad Request'}),400)

		task = json.loads(event["body"])
		response = 	updateTask(task)
		return createResponse(json.dumps({'msg': 'Task was updated successfully in database'}),200)

	elif event['httpMethod'] == 'DELETE':
		logger.info('## DELETE A TASK EVENT\r' + json.dumps(event, indent=2))
		if 'pathParameters' not in event or event['pathParameters'] == None or 'id' not in event['pathParameters']:
			return createResponse(json.dumps({'msg': 'Bad Request'}),400)

		id = event['pathParameters']['id']
		response = deleteTask(id)
		return createResponse(json.dumps({'msg': 'The task was deleted successfully from database'}),200)

	else:
		return createResponse(json.dumps({'msg': 'Bad Request'}),400)

def createTask(task):
	task['id'] = str(uuid.uuid1())
	task['status'] = 0
	task['is_major'] = 0

	try:
		response = table.put_item(Item=task)
	except ClientError as e:
		logger.error(e.response['Error']['Message'])
	else:
		return response

def getTask(id):
    try:
        response = table.get_item(Key={'id': id})
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
    else:
        return response


def getTasks():

    try:
        response = table.scan()
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
    else:
        return response.get('Items', [])

def updateTask(task):
    try:
        response = table.put_item(Item=task)
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
    else:
        return response


def deleteTask(id):
    try:
        response = table.delete_item(
            Key={ 'id': id },
        )
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
    else:
        return response


def createResponse(body,status):
	return {'body':body,'statusCode':status}


def handle_decimal_type(obj):
    if isinstance(obj, decimal.Decimal):
        if float(obj).is_integer():
            return int(obj)
        else:
            return float(obj)
    raise TypeError
