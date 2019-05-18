import json
import boto3
from botocore.exceptions import ClientError, ParamValidationError

def user_login(dynamodb, username, password):
	settings = dynamodb.get_item(
		TableName = 'users',
		Key = {
			'username': {'S': username}
		},
		ProjectionExpression = 'password'
	)
	if 'Item' not in settings:
		return {
			'success': 'False',
			'error_code': 401,
			'error': 'This username does not exist'
		}
	from passlib.hash import pbkdf2_sha256
	if pbkdf2_sha256.verify(password, settings['Item']['password']['S']):
		from secrets import token_urlsafe
		sessid = token_urlsafe(24)
		dynamodb.update_item(
			TableName = 'users',
			Key = {
				'username': {'S': username}
			},
			UpdateExpression = "ADD session_ids :value",
			ExpressionAttributeValues = {
				":value": {
					'SS': [sessid]
				}
			}
		)
		return {
			'success': True,
			'session_id': sessid
		}
	else:
		return {
			'success': 'False',
			'error_code': 401,
			'error': 'The password is incorrect'
		}

def message_new(dynamodb, username, title, markdown, rights, student_readable):
	if rights != 'teacher' and rights != 'admin':
		return {
			'success': False,
			'error_code': 401,
			'error': 'Only teachers and administrators can post'
		}
	import time
	from secrets import SystemRandom
	try:
		dynamodb.put_item(
			TableName = 'messages',
			Item = {
				'id': {'N': str(SystemRandom().randint(10000, 99999))},
				'title': {'S': title},
				'poster': {'S': username},
				'posttime': {'N': str(round(time.time() * 1000))},
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
		messages = dynamodb.scan(
			TableName='messages',
			ProjectionExpression='id, poster, posttime, title'
		)['Items']
	else:
		messages = dynamodb.scan(
			TableName = 'messages',
			FilterExpression = 'student = :true',
			ProjectionExpression = 'id, poster, posttime, title',
			ExpressionAttributeValues = {
				":true": {
					"BOOL": True
				}
			}
		)['Items']
	return_dict = {}
	for message in messages:
		return_dict[message['id']['N']] = {
			'title': message['title']['S'],
			'time': message['posttime']['N'],
			'poster': message['poster']['S']
		}
	return {
		'success': True,
		'messages': return_dict
	}

def message_view(dynamodb, username, user_rights, id):
	try:
		message = dynamodb.get_item(
			TableName = 'messages',
			Key = {
				'id': {'N': str(id)}
			},
			ProjectionExpression = 'markdown, student, form, attachments'
		)
		if 'Item' not in message:
			return {
				'success': False,
				'error_code': 404,
				'error': 'This message does not exist'
			}
		else:
			message = message['Item']

		if not message['student']['BOOL'] and user_rights != 'teacher' and user_rights != 'admin':
			return {
				'success': False,
				'error_code': 404,
				'error': 'This message does not exist'
			}

		return_dict = {
			'success': True,
			'text': message['markdown']['S']
		}

		if 'attachments' in message:
			return_dict['attachments'] = []
			for attachment in message['attachments']['L']:
				return_dict['attachments'].append({
					'name': attachment['M']['name']['S'],
					'link': attachment['M']['link']['S']
				})

		if 'form' in message:
			return_dict['form'] = []
			for form in message['form']['L']:
				form_dict = {
					'question': form['M']['question']['S'],
					'type': form['M']['type']['S']
				}
				if (form['M']['type']['S'] == 'mcq'):
					form_dict['options'] = form['M']['options']['SS']
				return_dict['form'].append(form_dict)

		return return_dict
	except ClientError as e:
		return {
			'success': False,
			'error_code': 500,
			'error': e.response['Error']['Message']
		}

def message_respond(dynamodb, username, user_rights, id, response):
	message = dynamodb.get_item(
		TableName = 'messages',
		Key = {
			'id': {'N': str(id)}
		},
		ProjectionExpression = 'form, student'
	)
	if 'Item' not in message:
		return {
			'success': False,
			'error_code': 404,
			'error': 'This message does not exist'
		}
	else:
		message = message['Item']

	if not message['student']['BOOL'] and user_rights != 'teacher' and user_rights != 'admin':
		return {
			'success': False,
			'error_code': 404,
			'error': 'This message does not exist'
		}
	error_dict = {
		'success': False,
		'error_code': 400,
		'error': 'Your JSON response does not match the schema'
	}
	if len(response) != len(message['form']['L']):
		return error_dict

	answer_array = []
	for i in range(0, len(response)):
		if message['form']['L'][i]['M']['type']['S'] == 'mcq':
			if int(response[i]) >= len(message['form']['L'][i]['M']['options']['SS']):
				return error_dict
		answer_array.append({
			'N' if message['form']['L'][i]['M']['type']['S'] == 'mcq' else 'S': str(response[i])
		})

	dynamodb.update_item(
		TableName = 'messages',
		Key = {
			'id': {'N': str(id)}
		},
		UpdateExpression = 'SET responses.#UID = :response',
		ExpressionAttributeNames = {
			'#UID': username
		},
		ExpressionAttributeValues = {
			":response": {
				"L": answer_array
			}
		}
	)
	return {
		'success': True
	}

def records_get(dynamodb, username):
	return {

	}

def learning_list(dynamodb, username):
	classes = dynamodb.scan(
		TableName = 'learning',
		ProjectionExpression = 'id, class_name, teacher, assignments',
		FilterExpression = 'contains(members, :username)',
		ExpressionAttributeValues = {
			":username": {
				"S": username
			}
		}
	)
	if 'Items' not in classes:
		return {
			'success': True
		}
	else:
		classes = classes['Items']
	return_dict = []
	for i in classes:
		assignments = []
		for assignment in i['assignments']['M']:
			assignments.append(i['assignments']['M'][assignment]['M']['name']['S'])
		return_dict.append({
			'teacher': i['teacher']['S'],
			'name': i['class_name']['S'],
			'code': i['id']['S'],
			'assignments': assignments
		})
	return return_dict

def learning_list_topics(dynamodb, username, class_id):
	topics = dynamodb.get_item(
		TableName = 'learning',
		Key = {
			'id': {'S': str(class_id)}
		},
		ProjectionExpression = 'topics, members, class_name, teacher'
	) 
	
	if 'Item' not in topics:
		return {
			'success': False,
			'error_code': 404,
			'error': 'This class does not exist'
		}
	topics = topics['Item']
	if username not in topics['members']['SS']:
		return {
			'success': False,
			'error_code': 404,
			'error': 'This class does not exist'
		}
	topics_list = []
	for topic in topics['topics']['M']:
		topics_list.append({
			'code': topic[1:],
			'name': topics['topics']['M'][topic]['M']['name']['S']
		})
	return {
		'name': topics['class_name']['S'],
		'teacher': topics['teacher']['S'],
		'tags': topics_list
	}

def learning_get_topic(dynamodb, username, class_id, topic_id):
	getTopic= dynamodb.get_item(
		TableName='learning',
		Key = {
			'id': {'S': str(class_id)}
		}, 
		ProjectionExpression='topics'
	)
	if 'Item' not in getTopic:
		return {
			'success': False,
			'error_code': 404,
			'error': 'This class does not exist'
		}
	getTopic = getTopic['Item']['topics']['M']['T' + topic_id]
	return_list = []
	for post in getTopic['M']['posts']['L']:
		attachments=[]
		if 'attachments' in post['M']:
			for attachment in post['M']['attachments']['L']:
				attachments.append({
					"name":attachment['M']['name']['S'],
					"link":attachment['M']['link']['S']
				})

		return_list.append({
			"title":post['M']['title']['S'],
			"description":post['M']['description']['S'],
			"timestamp":post['M']['timestamp']['N'],
			"attachments":attachments
		})
	return return_list

def learning_show_assignments(dynamodb, username, class_id):
	assignments = dynamodb.get_item(
		TableName = 'learning',
		Key = {
			'id': {'S': str(class_id)}
		},
		ProjectionExpression = 'members, assignments, class_name, teacher'
	)
	if 'Item' not in assignments:
		return {
			'success': False,
			'error_code': 404,
			'error': 'This class does not exist'
		}
	assignments = assignments['Item']
	if username not in assignments['members']['SS']:
		return {
			'success': False,
			'error_code': 404,
			'error': 'This assignment does not exist'
		}
	return_dict = {
		'success': True,
		'name': assignments['class_name']['S'],
		'teacher': assignments['teacher']['S'],
		'assignments': []
	}
	for assignment_code in assignments['assignments']['M'].keys():
		assignment_dict = {
			'code': assignment_code[1:],
			'name': assignments['assignments']['M'][assignment_code]['M']['name']['S'],
			# tags,
			'due': assignments['assignments']['M'][assignment_code]['M']['due']['N']
		}
		return_dict['assignments'].append(assignment_dict)
	return return_dict

def learning_assignment(dynamodb, username, class_id, assignment_id):
	assignments = dynamodb.get_item(
			TableName = 'learning',
			Key = {
				'id': {'S': str(class_id)}
			},
			ProjectionExpression = 'members, class_name, assignments.A' + str(assignment_id)
		)
	if 'Item' not in assignments:
		return {
			'success': False,
			'error_code': 404,
			'error': 'This class does not exist'
		}
	assignments = assignments['Item']
	if username not in assignments['members']['SS']:
		return {
			'success': False,
			'error_code': 404,
			'error': 'This assignment does not exist'
		}
	return_dict = {
		'name': assignments['assignments']['M']['A' + str(assignment_id)]['M']['name']['S'],
		'class': assignments['class_name']['S'],
		'questions': []
	}
	for question in assignments['assignments']['M']['A' + str(assignment_id)]['M']['questions']['L']:
		assignment_dict = {
			'question': question['M']['question']['S'],
			'type': question['M']['type']['S'],
			'marks': question['M']['marks']['N']
		}
		if question['M']['type']['S'] == 'mcq':
			assignment_dict['options'] = []
			for option in question['M']['options']['L']:
				assignment_dict['options'].append(option['S'])
		if 'image' in question['M']:
			assignment_dict['image'] = question['M']['image']['S']
		return_dict['questions'].append(assignment_dict)
	return return_dict

def learning_assignment_submit(dynamodb, username, assignment_id, answers):
	import time
	assignment = dynamodb.get_item(
		TableName = 'learning',
		Key = {
			'id': {'S': str(assignment_id)}
		},
		ProjectionExpression = 'members, assignments.A' + str(assignment_id) + '.questions'
	)
	if 'Item' not in assignment:
		return {
			'success': False,
			'error_code': 404,
			'error': 'This assignment does not exist'
		}
	else:
		assignment = assignment['Item']
	if username not in assignment['members']['SS']:
		return {
			'success': False,
			'error_code': 404,
			'error': 'This assignment does not exist'
		}
	error_dict = {
		'success': False,
		'error_code': 400,
		'error': 'Your JSON response does not match the schema'
	}
	if len(answers) != len(assignment['assignments']['M']['A' + str(assignment_id)]['M']['questions']['L']):
		return error_dict

	answer_array = []
	for i in range(0, len(answers)):
		if assignment['assignments']['M']['A' + str(assignment_id)]['M']['questions']['L'][i]['M']['type']['S'] == 'mcq':
			if int(answers[i]) >= len(assignment['assignments']['M']['A' + str(assignment_id)]['M']['questions']['L'][i]['M']['options']['L']):
				return error_dict
		answer_array.append({
			'N' if assignment['assignments']['M']['A' + str(assignment_id)]['M']['questions']['L'][i]['M']['type']['S'] == 'mcq' else 'S': str(answers[i])
		})
	dynamodb.update_item(
		TableName = 'learning',
		Key = {
			'id': {'S': str(assignment_id)}
		},
		UpdateExpression = 'SET assignment_submissions.#AID.#UID = :response',
		ExpressionAttributeNames = {
			'#AID': 'A' + str(assignment_id),
			'#UID': username
		},
		ExpressionAttributeValues = {
			":response": {
				"M": {
					"submission_time": {"N": str(round(time.time() * 1000))},
					"answers": {"L": answer_array}
				}
			}
		}
	)
	return {
		'success': True
	}

def library_index(dynamodb, username):
	return {
		'success': True,
		'school_code': dynamodb.get_item(
			TableName = 'users',
			Key = {
				'username': {'S': username}
			},
			ProjectionExpression = 'library.school.school_code'
		)['Item']['library']['M']['school']['M']['school_code']['S']
	}

def library_books(dynamodb, username, library, library_code):
	# library_code is "nlb" or "xxxx" (school code)
	if library != 'school' and library != 'nlb':
		return {
			'success': False,
			'error_code': 400,
			'error': 'Library can only be "school" or "nlb"'
		}
	if library == 'nlb' and library_code != 'nlb':
		return {
			'success': False,
			'error_code': 400,
			'error': 'Library_code can only be "nlb"'
		}
	if library == 'school' and (library_code.isdigit() == False or len(library_code) != 4):
		return {
			'success': False,
			'error_code': 400,
			'error': 'Library_code can only be a four-digit integer (including leading zeros)'
		}

	books = dynamodb.get_item(
		TableName = 'users',
		Key = {
			'username': {'S': username}
		},
		ProjectionExpression = 'library.' + library + '.borrowed'
	)
	if 'Item' not in books:
		return {
			'success': True,
			'books': []
		}
	else:
		books = books['Item']['library']['M'][library]['M']['borrowed']['L']
	id_list = []
	for i in books:
		if i['M']['returned']['BOOL'] == True:
			books.remove(i)
	for i in books:
		id_list.append({'id': i['M']['id']})
	if len(id_list) == 0:
		return {
			'success': True,
			'books': []
		}
	book_data = dynamodb.batch_get_item(
		RequestItems = {
			'books_' + library_code: {
				'Keys': id_list,
				'ProjectionExpression': 'id, book_name, author, synopsis'
			}
		}
	)['Responses']['books_nlb']
	book_data_formatted = {}
	for book in book_data:
		book_data_formatted[book['id']['S']] = {
			'name': book['book_name']['S'],
			'synopsis': book['synopsis']['S'],
			'author': book['author']['S']
		}
	return_list = []
	for book in books:
		return_list.append({
			'due': book['M']['due']['N'],
			**book_data_formatted[book['M']['id']['S']]
		})

	return return_list

def settings_get(dynamodb, username):
	settings = dynamodb.get_item(
		TableName = 'users',
		Key = {
			'username': {'S': username}
		},
		ProjectionExpression = 'address, email, phone, theme, full_name'
	)['Item']
	return {
		'success': True,
		'address': settings['address']['S'],
		'email': settings['email']['S'],
		'phone': settings['phone']['N'],
		'theme': settings['theme']['S'],
		'name': settings['full_name']['S'],
	}

def settings_update(dynamodb, username, key, value):
	if key not in {'address', 'email', 'phone', 'theme', 'password'}:
		return {
			'success': False,
			'error_code': 400,
			'error': 'Only address, email, phone, theme, and password can be edited'
		}
	if key == 'password':
		if len(value) < 8:
			return {
				'success': False,
				'error_code': 400,
				'error': 'Your must be at least 8 characters long'
			}
		from passlib.hash import pbkdf2_sha256
		value = pbkdf2_sha256.hash(value, rounds = 25000, salt_size = 16)
	if key == 'theme' and value not in {'light', 'dark'}:
		return {
			'success': False,
			'error_code': 400,
			'error': 'Only light and dark themes are available'
		}
	if key == 'phone':
		if not value.isdigit():
			return {
				'success': False,
				'error_code': 400,
				'error': 'Only numbers are allowed for phone numbers'
			}
		if int(value) < 80000000 or int(value) > 99999999:
			return {
				'success': False,
				'error_code': 400,
				'error': 'Only 8-digit mobile phone numbers are allowed'
			}
	if key == 'email':
		import re
		if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
			return {
				'success': False,
				'error_code': 400,
				'error': 'Invalid email format'
			}
	dynamodb.update_item(
		TableName = 'users',
		Key = {
			'username': {'S': username}
		},
		UpdateExpression = "SET #KEY = :value",
		ExpressionAttributeNames = {
			'#KEY': key
		},
		ExpressionAttributeValues = {
			":value": {
				"N" if key == 'phone' else 'S': value
			}
		}
	)
	return {
		'success': True
	}
	
def lambda_handler(param, context):
	dynamodb = boto3.client('dynamodb')
	if param['user']['logged_in'] == False:
		if param['request']['type'] == 'user_login':
			return user_login(dynamodb, param['request']['username'], param['request']['password'])
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
				return message_respond(dynamodb, param['user']['username'], user_data['rights']['S'], param['request']['id'], param['request']['response'])
			elif param['request']['type'] == 'records_get':
				return records_get(dynamodb, param['user']['username'])
			elif param['request']['type'] == 'learning_list':
				return learning_list(dynamodb, param['user']['username'])
			elif param['request']['type'] == 'learning_list_topics':
				return learning_list_topics(dynamodb, param['user']['username'], param['request']['id'])
			elif param['request']['type'] == 'learning_get_topic':
				return learning_get_topic(dynamodb, param['user']['username'], param['request']['class_id'], param['request']['topic_id'])
			elif param['request']['type'] == 'learning_show_assignments':
				return learning_show_assignments(dynamodb, param['user']['username'], param['request']['class_id'])
			elif param['request']['type'] == 'learning_assignment':
				return learning_assignment(dynamodb, param['user']['username'], param['request']['class_id'], param['request']['assignment_id'])
			elif param['request']['type'] == 'learning_assignment_submit':
				return learning_assignment_submit(dynamodb, param['user']['username'], param['request']['id'], param['request']['answers'])
			elif param['request']['type'] == 'library_index':
				return library_index(dynamodb, param['user']['username'])
			elif param['request']['type'] == 'library_books':
				return library_books(dynamodb, param['user']['username'], param['request']['library'], param['request']['library_code'])
			elif param['request']['type'] == 'settings_get':
				return settings_get(dynamodb, param['user']['username'])
			elif param['request']['type'] == 'settings_update':
				return settings_update(dynamodb, param['user']['username'], param['request']['key'], param['request']['value'])
			else:
				return {
					'success': False,
					'error': 404
				}
		else:
			return {
				'success': False,
				'error_code': 401,
				'error': 'This session ID is invalid'
			}