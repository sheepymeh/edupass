import json
import boto3
import random

# def user_create(username, password, name, gender, birthdate, address):
# 	import passlib as pwd_context
# 	dynamodb = boto3.resource('dynamodb')
# 	table = dynamodb.Table('messages')
# 	table.put_item(
# 		Item = {
# 			'username': username
# 			'name': name,
# 			'password': '1',
# 			'timestamp': 1558012701695
# 		}
# 	)

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
			ProjectionExpression = 'session_ids, role, classes'
		)
		if (param['user']['session_id'] in user_data['Item']['session_ids']['SS'])
			return {
				'message_new': message_new(user_data['Item']['role']['S'], param['request']['title'], param['request']['from'], param['request']['timestamp']),
				'message_list': message_list(user_data['Item']['role']['S']),
				'message_view': message_view(param['user']['username'], param['request']['id']),
				'message_respond': message_respond(param['user']['username'], param['request']['id'], param['request']['response'])

				'records_get': records_get(param['user']['username']),
				# 'records_update'

				# 'counseling'

				# we'll need a function to check that the student is actually in the class
				'learning_list': learning_list(param['user']['username'], user_data['Item']['classes']['NS']),
				'learning_show_class': learning_show_class(param['request']['id'], param['request']['id'])
				'learning_show_assignments': learning_show_assignments(param['user']['username'], param['request']['id']),
				'learning_assignment': learning_assignment(param['user']['username'], param['request']['id']),
				'learning_assignment_submit': learning_assignment_submit(param['user']['username'], param['request']['id'], param['request']['answers']),

				'library_index': library_index(param['user']['username']),
				'library_fines': library_fines(param['user']['username']),
				'library_books': library_books(param['user']['username']),
				'library_recommendations': library_recommendations(param['user']['username']),

				'settings_get': settings_get(param['user']['username']),
				'settings_update': settings_update(param['user']['username']),
				# ^^ how?
			}.get(param['request']['type'], {
				'success': False,
				'error': 404
			})
		else:
			return 'no'
	# table = dynamodb.Table('messages')
	# table.put_item(
	# 	Item = {
	# 		'id': random.SystemRandom().randint(10000, 99999),
	# 		'title': 'A Certain Dumb Cunt: A Certain Miagical Index Fan Fiction',
	# 		'from': 'Jeron Sia',
	# 		'timestamp': 1558012701695
	# 	}
	# )