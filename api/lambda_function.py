import json
import boto3

def user_login():
	return {

	}

def user_create():
	return {

	}

def user_forget():
	return {

	}

def message_new(dynamodb, rights, title, username, markdown):
	import time
	from random import SystemRandom
	dynamodb.put_item(
		TableName = 'messages',
		Item = {
			'id': {'N': SystemRandom().randint(10000, 99999)},
			'title': {'S': title},
			'from': {'S': 'Jeron Sia'},
			'timestamp': {'N': int(round(time.time() * 1000))}
		}
	)
	return {
		'success': True
	}

def message_list():
	return {

	}

def message_view(dynamodb, username, rights, id):
	message = dynamodb.get_item(
			TableName = 'messages',
			Key = {
				'username': {'S': username}
			},
			ProjectionExpression = 'session_ids, rights, classes'
		)
	# 1. get message
	# 2. mark as read
	return {

	}

def message_respond():
	return {

	}

def records_get():
	return {

	}

def learning_list():
	return {

	}

def learning_show_class():
	return {

	}

def learning_show_assignments():
	return {

	}

def learning_assignment():
	return {

	}

def learning_assignment_submit():
	return {

	}

def library_index():
	return {

	}

def library_fines():
	return {

	}

def library_books():
	return {

	}

def library_recommendations():
	return {

	}

def settings_get():
	return {

	}

def settings_update():
	return {

	}



def lambda_handler(param, context):
	dynamodb = boto3.client('dynamodb')
	if (param['user']['logged_in'] == False):
		# from passlib.hash import pbkdf2_sha256
		return {
			'user_login': user_login(param['request']['username'], param['request']['password']),
			'user_create': user_create(param['request']['username'], param['request']['password'], param['request']['name'], param['request']['gender'], param['request']['birthdate'], param['request']['address']),
			'user_forget': user_forget(param['request']['username']),
		}.get(param['request']['type'], {
			'success': False,
			'error': 404
		})
	else:
		user_data = dynamodb.get_item(
			TableName = 'users',
			Key = {
				'username': {'S': param['user']['username']}
			},
			ProjectionExpression = 'session_ids, rights, classes'
		)
		if (param['user']['session_id'] in user_data['Item']['session_ids']['SS']):
			return {
				'message_new': message_new(dynamodb, user_data['Item']['rights']['S'], param['request']['title'], param['user']['username'], param['request']['markdown']),
				'message_list': message_list(dynamodb, user_data['Item']['rights']['S']),
				'message_view': message_view(dynamodb, param['user']['username'], user_data['Item']['rights']['S'], param['request']['id']),
				'message_respond': message_respond(dynamodb, param['user']['username'], param['request']['id'], param['request']['response']),

				'records_get': records_get(dynamodb, param['user']['username']),
				# 'records_update'

				# 'counseling'

				# we'll need a function to check that the student is actually in the class
				'learning_list': learning_list(dynamodb, param['user']['username'], user_data['Item']['classes']['NS']),
				'learning_show_class': learning_show_class(dynamodb, param['request']['id'], param['request']['id']),
				'learning_show_assignments': learning_show_assignments(dynamodb, param['user']['username'], param['request']['id']),
				'learning_assignment': learning_assignment(dynamodb, param['user']['username'], param['request']['id']),
				'learning_assignment_submit': learning_assignment_submit(dynamodb, param['user']['username'], param['request']['id'], param['request']['answers']),

				'library_index': library_index(dynamodb, param['user']['username']),
				'library_fines': library_fines(dynamodb, param['user']['username']),
				'library_books': library_books(dynamodb, param['user']['username']),
				'library_recommendations': library_recommendations(dynamodb, param['user']['username']),

				'settings_get': settings_get(dynamodb, param['user']['username']),
				'settings_update': settings_update(dynamodb, param['user']['username']),
				# ^^ how?
			}.get(param['request']['type'], {
				'success': False,
				'error': 404
			})
		else:
			return 'no'