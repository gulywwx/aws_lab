import base64
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
table = dynamodb.Table(os.environ['USER_TABLE'])


def lambda_handler(event, context):
	logger.info('## EVENT\r' + json.dumps(event, indent=2))
	if event['httpMethod'] == 'GET':
		if 'pathParameters' not in event or event['pathParameters'] == None:
			response = getUsers()
			return createResponse(json.dumps(response, indent=2, default=handle_decimal_type),200)
		else:
			if 'id' not in event['pathParameters']:
				return createResponse(json.dumps({'msg': 'Bad Request'}),400)
			id = event['pathParameters']['id']
			response = getUser(id)
			if ('Item' not in response):
				return createResponse(json.dumps({'msg': 'The user not found'}),404)
			return createResponse(json.dumps(response['Item'], indent=2, default=handle_decimal_type),200)

	elif event['httpMethod'] == 'POST':
		if ('body' not in event or event['body'] == None or 'email' not in event['body']) or 'password' not in event['body']:
			return createResponse(json.dumps({'msg': 'Bad Request'}),400)

		user = json.loads(event["body"])
		response = 	createUser(user)
		return createResponse(json.dumps({'msg': 'A new user was saved successfully in database'}),200)

	elif event['httpMethod'] == 'PUT':
		if ('body' not in event or event['body'] == None or 'email' not in event['body'] or  'id' not in event['body']):
			return createResponse(json.dumps({'msg': 'Bad Request'}),400)

		user = json.loads(event["body"])
		response = 	updateUser(user)
		return createResponse(json.dumps({'msg': 'The user was updated successfully in database'}),200)

	elif event['httpMethod'] == 'DELETE':
		logger.info('## DELETE A TASK EVENT\r' + json.dumps(event, indent=2))
		if 'pathParameters' not in event or event['pathParameters'] == None or 'id' not in event['pathParameters']:
			return createResponse(json.dumps({'msg': 'Bad Request'}),400)

		id = event['pathParameters']['id']
		response = deleteUser(id)
		return createResponse(json.dumps({'msg': 'The user was deleted successfully from database'}),200)

	else:
		return createResponse(json.dumps({'msg': 'Bad Request'}),400)



def createUser(user):
	user['id'] = str(uuid.uuid1())
	# user['password'] = encode('mypassword',user['password'])

	try:
		response = table.put_item(Item=user)
	except ClientError as e:
		logger.error(e.response['Error']['Message'])
	else:
		return response

def getUser(id):
	try:
		response = table.get_item(Key={'id': id})
		response['Item']['password']  = '******'
	except ClientError as e:
		logger.error(e.response['Error']['Message'])
	else:
		return response


def getUsers():
	try:
		response = table.scan()
		for i in response['Items']:
			i['password'] = '******'

	except ClientError as e:
		logger.error(e.response['Error']['Message'])
	else:
		return response.get('Items', [])

def updateUser(user):
    try:
        response = table.put_item(Item=user)
    except ClientError as e:
        logger.error(e.response['Error']['Message'])
    else:
        return response


def deleteUser(id):
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

# def encode(key, clear):
#     enc = []
#     for i in range(len(clear)):
#         key_c = key[i % len(key)]
#         enc_c = chr((ord(clear[i]) + ord(key_c)) % 256)
#         enc.append(enc_c)
#     return base64.urlsafe_b64encode("".join(enc))

# def decode(key, enc):
#     dec = []
#     enc = base64.urlsafe_b64decode(enc)
#     for i in range(len(enc)):
#         key_c = key[i % len(key)]
#         dec_c = chr((256 + ord(enc[i]) - ord(key_c)) % 256)
#         dec.append(dec_c)
#     return "".join(dec)
