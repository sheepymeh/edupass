import json
import boto3
from botocore.exceptions import ClientError, ParamValidationError

def user_login(dynamodb, username, password):
	return {

	}

def user_create(dynamodb, username, password, name, gender, birthdate, address):
	return {

	}

def user_forget(dynamodb, username):
	return {

	}

def message_new(dynamodb, username, title, markdown, rights, student_readable):
	if rights != 'teacher' and rights != 'admin':
		return {
			'success': False,
			'error_code': 401,
			'error': 'Only teachers and administrators can post'
		}
	import time
	from random import SystemRandom
	try:
		dynamodb.put_item(
			TableName = 'messages',
			Item = {
				'id': {'N': str(SystemRandom().randint(10000, 99999))},
				'title': {'S': title},
				'poster': {'S': username},
				'timestamp': {'N': str(round(time.time() * 1000))},
				'markdown': {'S': markdown},
				'student': {'BOOL': student_readable}
			},
			ConditionExpression = 'attribute_not_exists(id)'
		)
		return {
			'success': True
		}
	except dynamodb.exceptions.ConditionalCheckFailedException:
		message_new(dynamodb, username, title, markdown, rights, student_readable)
	except ClientError as e:
		return {
			'success': False,
			'error_code': 500,
			'error': e.response['Error']['Message']
		}

def message_list(dynamodb, rights):
	if rights == 'teacher' or rights=='admin':
		return dynamodb.scan(
			TableName='messages',
			ProjectionExpression='id, poster, timee, title'
		)['Item']['']
	return dynamodb.scan(
		TableName='messages',
		FilterExpression='student = 1',
		ProjectionExpression='id, poster, timee, title'
	)['Item']

def message_view(dynamodb, username, user_rights, id):
	try:
		message = dynamodb.get_item(
			TableName = 'messages',
			Key = {
				'id': {'N': str(id)}
			},
			ProjectionExpression = 'markdown, student'
		)
		if 'Item' not in message:
			return {
				'success': False,
				'error_code': 404,
				'error': 'This message does not exist'
			}
		else:
			message = message['Item']

		return 1
		return message

		if message['student']['bool'] and user_rights != 'teacher' and user_rights != 'admin':
			return {
				'success': False,
				'error_code': 404,
				'error': 'This message does not exist'
			}

	except ClientError as e:
		return False

def message_respond(dynamodb, username, id, response):
	return {

	}

def records_get(dynamodb, username):
	return {

	}

def learning_list(dynamodb, username, classes_list):
	return {

	}

def learning_show_class(dynamodb, username, class_id):
	return {

	}

def learning_show_assignments(dynamodb, username, class_id):
	return {

	}

def learning_assignment(dynamodb, username, assignment_id):
	return {

	}

def learning_assignment_submit(dynamodb, username, assignment_id, answers):
	return {

	}

def library_index(dynamodb, username):
	return {

	}

def library_fines(dynamodb, username):
	return {

	}

def library_books(dynamodb, username):
	return {

	}

def library_recommendations(dynamodb, username):
	return {

	}

def settings_get(dynamodb, username):
	return {

	}

def settings_update(dynamodb, username):
	return {

	}

def lambda_handler(param, context):
	dynamodb = boto3.client('dynamodb')
	if param['user']['logged_in'] == False:
		# from passlib.hash import pbkdf2_sha256
		if param['request']['type'] == 'user_login':
			return user_login(dynamodb, param['request']['username'], param['request']['password'])
		elif param['request']['type'] == 'user_create':
			return user_create(dynamodb, param['request']['username'], param['request']['password'], param['request']['name'], param['request']['gender'], param['request']['birthdate'], param['request']['address'])
		elif param['request']['type'] == 'user_forget':
			return user_forget(dynamodb, param['request']['username'])
		else:
			return {
				'success': False,
				'error': 404
			}
	else:
		user_data = dynamodb.get_item(
			TableName = 'users',
			Key = {
 				'username': {'S': param['user']['username']}
			},
			ProjectionExpression = 'session_ids, rights, classes'
		)
		if 'Item' not in user_data:
			return {
				'success': False,
				'error_code': 401,
				'error': 'This username does not exist'
			}
		else:
			user_data = user_data['Item']

		if param['user']['session_id'] in user_data['session_ids']['SS']:
			if param['request']['type'] == 'message_new':
				return message_new(dynamodb, param['user']['username'], param['request']['title'], param['request']['markdown'], user_data['rights']['S'], param['request']['student'])
			elif param['request']['type'] == 'message_list':
				return message_list(dynamodb, user_data['rights']['S'])
			elif param['request']['type'] == 'message_view':
				return message_view(dynamodb, param['user']['username'], user_data['rights']['S'], param['request']['id'])
			elif param['request']['type'] == 'message_respond':
				return message_respond(dynamodb, param['user']['username'], param['request']['id'], param['request']['response'])
			elif param['request']['type'] == 'records_get':
				return records_get(dynamodb, param['user']['username'])
			elif param['request']['type'] == 'learning_list':
				return learning_list(dynamodb, param['user']['username'], user_data['classes']['NS'])
			elif param['request']['type'] == 'learning_show_class':
				return learning_show_class(dynamodb, param['user']['username'], param['request']['id'])
			elif param['request']['type'] == 'learning_show_assignments':
				return learning_show_assignments(dynamodb, param['user']['username'], param['request']['id'])
			elif param['request']['type'] == 'learning_assignment':
				return learning_assignment(dynamodb, param['user']['username'], param['request']['id'])
			elif param['request']['type'] == 'learning_assignment_submit':
				return learning_assignment_submit(dynamodb, param['user']['username'], param['request']['id'], param['request']['answers'])
			elif param['request']['type'] == 'library_index':
				return library_index(dynamodb, param['user']['username'])
			elif param['request']['type'] == 'library_fines':
				return library_fines(dynamodb, param['user']['username'])
			elif param['request']['type'] == 'library_books':
				return library_books(dynamodb, param['user']['username'])
			elif param['request']['type'] == 'library_recommendations':
				return library_recommendations(dynamodb, param['user']['username'])
			elif param['request']['type'] == 'settings_get':
				return settings_get(dynamodb, param['user']['username'])
			elif param['request']['type'] == 'settings_update':
				return settings_update(dynamodb, param['user']['username'])
			else:
				return {
					'success': False,
					'error': 404
				}
		if 'Item' not in user_data:
			return {
				'success': False,
				'error_code': 401,
				'error': 'This session ID is invalid'
			}