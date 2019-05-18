# Lambda API Endpoints Documentation

## Logged In Componenets

### Temporary Credentials
**Username:** ```T0372813C```  
**Session ID:** ```long_id_no_one_will_ever_guess```

### Request Format
```json
{
	"user": {
		"logged_in": "true",
		"session_id": "Insert Session ID from cookie",
		"username": "Insert NRIC from cookie"
	},
	"request": {
		"type": "Request Type (see headers)",
		"other_parameters": "Parameter Value (request type specific)"
	}
}
```

### Response Format
```json
{
	"success": bool,
	"other_responses": "Response Value (request type specific)"
}
```

### Shared Error Codes

#### Invalid Session ID
```json
{
	"success": false,
	"error_code": 401,
	"error": "This session ID is invalid"
}
```
Solve by logging in again

### message_new
_Should **not** be used in student environment anyways, just a debugging tool_
**Purpose:** creates new message  
**Security Clearance:** Admins/Teachers only

**Parameters:**
* title // String, title of message
* markdown // String, body of message in Markdown
* student // Boolean, set to False to disable access to students

**Response:**
* No specific responses

**Errors:**
* 401 // Unauthorized
	* Error Message: "Only teachers and administrators can post" // A student is trying to post

**Sample Request:**
```json
{
  "user": {
    "logged_in": "true",
    "session_id": "long_id_no_one_will_ever_guess",
    "username": "T0372813C"
  },
  "request": {
    "type": "message_new",
    "title": "A Certain Dumb Dumb: A Certain Miagical Index Fan Fiction",
    "markdown": "# jeron is big weebment",
    "student": false
  }
}
```

### message_list
_Drop-in replacement for const MESSAGES_OBJECT in messages.html_
**Purpose:** lists all messages available  
**Security Clearance:** automatically hides privileged posts from students

**Parameters:**
* No specific parameters

**Response:**
```json
{
	"message_id": {
		"title": "Message Title",
		"time": "Posting Timestamp",
		"user": "Sender"
	},
	"other_message_id": {
		...
	},
	...
}
```
* message_id // Integer, 5-digit identifier unique to each message
* title // String, title of message
* time // Integer, unix epoch time (with milliseconds) of posting
* user // String, NRIC (username) of sender

**Errors:**
* No specific errors

**Sample Request:**
```json
{
  "user": {
    "logged_in": "true",
    "session_id": "long_id_no_one_will_ever_guess",
    "username": "T0372813C"
  },
  "request": {
    "type": "message_list"
  }
}
```

### message_view
_Drop-in replacement for const MESSAGE in messages.html_
**Purpose:** returns Markdown of specific message  
**Security Clearance:** automatically hides privileged posts from students

**Parameters:**
* id // Integer, 5-digit identifier unique to each message

**Response:**
```json
{
	"text": "Markdown Body",
	"attachments": [
		{
			"name": "File Name",
			"link": "Link to S3"
		},
		...
	],
	"form": [
		{
			"question": "Question",
			"type": "oe"
		},
		{
			"question": "Question",
			"type": "mcq",
			"options": [
				"Option 1",
				"Option 2",
				...
			]
		},
		...
	]
}
```
* text // String, Markdown representation of body
* attachments // Array, 1 attachment per object
	* name // String, name of file
	* link // String, link to file hosted on S3
* form // Array, 1 question per object
	* question // String, question to be asked
	* type // String, "oe" is open-ended; "mcq" is multiple choice
	* options // Array, options for selection (only when type == "mcq")

**Errors:**
* 404 // Not Found
	* Error Message: "This message does not exist" // The message ID supplied does not exist, or a student is trying to access a privilged message

```json
{
  "user": {
    "logged_in": "true",
    "session_id": "long_id_no_one_will_ever_guess",
    "username": "T0372813C"
  },
  "request": {
    "type": "learning_get_topic",
    "class_id": "12345",
    "topic_id": "T123456"
  }
}
```

### message_respond
_Currently unimplemented in messages.html_
**Purpose:** Respond to forms in messages
**Security Clearence:** All

**Parameters:**
* id // Integer, 5-digit identifier unique to each message
* response // Array with all fields, one string/number to field:
	```json
	[
		"open-ended response",
		"1"
	]
	```
	responds to
	```json
	[
		{
			"question": "Open Ended Question",
			"type": "oe"
		},
		{
			"question": "MCQ Question",
			"type": "mcq",
			"options": [
				"Option 1",
				"Option 2",
				"Option 3"
			]
		}
	]
	```
	Question numbers are 1:1. Option 1 refers to the 2nd item in the options array

**Response:**
* No specific responses

**Errors:**
* 400 // Bad Request
	* Error Message: "Your JSON response does not match the schema" // Too many/too little answers, or tried submitting open-ended question type for MCQ question
* 404 // Not Found
	* Error Message: "This message does not exist" // Check the ```id``` parameter, or a student is accessing a privileged message

**Sample Request:**
```json
{
  "user": {
    "logged_in": "true",
    "session_id": "long_id_no_one_will_ever_guess",
    "username": "T0372813C"
  },
  "request": {
    "type": "message_respond",
    "id": 43322,
    "response": [
      "open-ended response",
      "2"
    ]
  }
}
```

### learning_list
_**CONDENSED (different)** replacement for const MESSAGES_OBJECT in messages.html_
**Purpose:** lists all joined classes  
**Security Clearance:** automatically shows only joined classes

**Parameters:**
* No specific parameters

**Response:**
```json
[
	{
		"code": "Class Code",
		"teacher": "Teacher Username",
		"name": "Class Name",
		"assignments": ["Assignment Name", ...]
	},
	...
]
```
* class_id // Integer, 5-digit class code unique to each class
* teacher // String, username of hosting teacher
* name // String, name of class

**Errors:**
* No specific errors

**Sample Response:**
```json
{
  "user": {
    "logged_in": "true",
    "session_id": "long_id_no_one_will_ever_guess",
    "username": "T0372813C"
  },
  "request": {
    "type": "learning_list"
  }
}
```

### learning_show_assignments
_Drop-in replacement for const CLASS in assignments.html_
**Purpose:** lists assignments in a certain class  
**Security Clearance:** automatically shows only assignments of joined classes

**Parameters:**
* class_id // Integer, 5-digit class code unique to each class

**Response:**
```json
{
	"name": "Class Name",
	"teacher": "Teacher Name",
	"assignments": [
		{
			"code": "12345",
			"name": "Hyper Easy Mole Concept Revision",
			"due": {
				"N": "1557796568966"
			}
		}
	]
}
```
* name // String, name of class
* teacher // String, username of hosting teacher
* assignments // Array, 1 assignment per object
	* code // Integer, 6-digit 6-digit class code unique to each assignment (globally assigned, not attached to class)
	* name // String, name of specific assignment
	* due // Integer, unix epoch time (with milliseconds) of due date

**Errors:**
* 404 // Not found
	* Error Message: "This class does not exist" // The class ID supplied is invalid, or the student has not joined that class

**Sample Request:**
```json
{
  "user": {
    "logged_in": "true",
    "session_id": "long_id_no_one_will_ever_guess",
    "username": "T0372813C"
  },
  "request": {
    "type": "learning_show_assignments",
    "class_id": "12345",
    "assignment_id": "12346"
  }
}
```

### learning_assignment
_Drop-in replacement for const QUESTIONS in assignment.html_
**Purpose:** shows details of one assignment
**Security Clearance:** automatically shows only assignments of joined classes

**Parameters:**
* class_id // Integer, 5-digit class code unique to each class
* assignment_id // Integer, 6-digit class code unique to each assignment (globally assigned, not attached to class)

**Response:**
```json
{
	"name": "Hyper Easy Mole Concept Revision",
	"class": "4S3 Chemistry",
	"questions": [
		{
			"question": "Which line corresponds to the reaction in higher temperature?",
			"type": "mcq",
			"marks": "1",
			"options": [
				"Blue Line",
				"Pink Line"
			],
			"image": "https://www.edplace.com/userfiles/image/Rate%20of%20Reaction%202.jpg"
		}
	]
}
```
* name // String, name of class
* teacher // String, username of hosting teacher
* assignments // Array, 1 assignment per object
	* code // Integer, 6-digit 6-digit class code unique to each assignment (globally assigned, not attached to class)
	* name // String, name of specific assignment
	* due // Integer, unix epoch time (with milliseconds) of due date

**Errors:**
* 404 // Not found
	* Error Message: This class does not exist // The class ID supplied is invalid, or the student has not joined that class

**Sample Request:**
```json
{
  "user": {
    "logged_in": "true",
    "session_id": "long_id_no_one_will_ever_guess",
    "username": "T0372813C"
  },
  "request": {
    "type": "learning_assignment",
    "class_id": "12345",
    "assignment_id": "12345"
  }
}
```

### library_index
**Purpose:** returns school code of student
**Security Clearance:** all

**Response:**
* school_code // Integer, school code

**Sample Request:**
```json
{
  "user": {
    "logged_in": "true",
    "session_id": "long_id_no_one_will_ever_guess",
    "username": "T0372813C"
  },
  "request": {
    "type": "library_index"
  }
}
```

### library_recommendations
Not implemented due to time constraints