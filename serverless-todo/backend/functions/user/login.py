import datetime
import json
import logging
import os

import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

import jwt

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(os.environ['USER_TABLE'])

def lambda_handler(event, context):
	try:
		body = json.loads(event['body'])

		email = body['email']
		password = body['password']

		if email is not None and password is not None:
			response = getUser(email)
			if json.dumps(response['Items']) == '[]':
				return {
					"statusCode": 200,
					"body": json.dumps({
						"msg": "Error ! The user Not Found",
						"data": None,
						"code":-1
					})
				}

			if response['Items'][0]['password'] == password:
				result = {"id":response['Items'][0]['id'],"first_name":response['Items'][0]['first_name'],"last_name":response['Items'][0]['last_name']}
				jwt_info = create_access_token(result)
				return {
					"statusCode": 200,
					"body": json.dumps({
						"msg": "Welcome !",
						"data": {
							"token": jwt_info
						}
					})
				}
			else:
				return {
					"statusCode": 400,
					"body": json.dumps({
						"msg": "Error ! The password is incorrect",
						"data": None,
						"code": -1
					})
				}

		else:
			return {
				"statusCode": 400,
				"body": json.dumps({
					"msg": "Error !",
					"data": None
				})
			}
	except:
		return {
			"statusCode": 400,
			"body": json.dumps({
				"msg": "Something went wrong. Unable to parse data !"
			})
		}


def getUser(email):
    try:
        response = table.query( IndexName='emailIndex',KeyConditionExpression=Key('email').eq(email))

    except ClientError as e:
        logger.error(e.response['Error']['Message'])
    else:
        return response



def create_access_token(result):
    # Returns new JWT Token.
    jwt_info = jwt.encode({
        "id": str(result["id"]),
        "first_name": result["first_name"],
        "last_name": result["last_name"],
        "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=300)}, os.environ['SECRET_KEY'])

    return jwt_info


def refresh_token(token):
    # Refresh Token if the token hasn't expired.
    try:
        result = jwt.decode(token, os.environ['SECRET_KEY'], algorithms=["HS256"])
        jwt_info = jwt.encode({**result, "exp": datetime.datetime.utcnow() + datetime.timedelta(seconds=300)},
                              os.environ['SECRET_KEY'])

        return {"status": True, "data": jwt_info, "message": None}
    except jwt.exceptions.DecodeError:
        return {"status": False, "data": None, "message": "Unable to decode data !"}
    except jwt.ExpiredSignatureError:
        return {"status": False, "data": None, "message": "Token has expired !"}
