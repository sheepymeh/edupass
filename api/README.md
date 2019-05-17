# Lambda API Endpoints Documentation

## Logged In Componenets

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
	"other_responses": "Response Value (request type specific)
}
```

### Shared Error Codes

#### Invaled Session ID
```json
{
	"success": False,
	"error_code": 401,
	"error": "This session ID is invalid"
}
```
Solve by logging in again

### message_new
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

### message_list
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

### message_view
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

### learning_list
**Purpose:** lists all joined classes  
**Security Clearance:** automatically shows only joined classes

**Parameters:**
* No specific parameters

**Response:**
```json
{
	"class_id": {
		"teacher": "Teacher Username",
		"name": "Class Name"
	},
	...
}
```
* class_id // Integer, 5-digit class code unique to each class
* teacher // String, username of hosting teacher
* name // String, name of class

**Errors:**
* No specific errors

### learning_show_assignments
**Purpose:** lists assignments in a certain class  
**Security Clearance:** automatically shows only assignments of joined classes

**Parameters:**
* class_id // Integer, 5-digit class code unique to each class
<!-- * assignment_id // Integer, 6-digit class code unique to each assignment (globally assigned, not based on class) -->

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

### learning_show_assignments
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
	* Error Message: "This class does not exist" // The class ID supplied is invalid, or the student has not joined that class