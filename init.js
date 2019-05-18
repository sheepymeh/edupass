const COOKIE = {
	set: (name, value, seconds) => {
		const d = new Date();
		d.setTime(d.getTime() + seconds * 1000);
		document.cookie = `${name}=${value};expires=${d.toUTCString()};path=/`
	},
	get: name => {
		name += '=';
		const cookies = document.cookie.split(';');
		for (let i = cookies.length - 1; i >= 0; i -= 1) {
			const cookie = cookies[i].trim();
			if (cookie.includes(name)) return cookie.substring(name.length, cookie.length);
		}
		return false;
	},
	delete: name =>
		document.cookie = `${name}=expired;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`
}

if (!COOKIE.get('sessid') || !COOKIE.get('username')) window.location.href = 'http://sheepymeh.github.io/edupass/login.html';

const LINK = document.createElement("link");
LINK.type = "text/css";
LINK.rel = "stylesheet";
let set = false;
if (COOKIE.get('theme')) {
	LINK.href = `../themes/${window.location.href.split('/').slice(-2)[0]}/${COOKIE.get('theme')}_theme.css`;
	document.head.appendChild(LINK);
	set = true;
}

// This user is limited to the EduPass Lambda function, which handles authorization within the function
AWS.config.accessKeyId = 'AKIAQF4IUI6AIH5HNSOF';
AWS.config.secretAccessKey = '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';
AWS.config.region = 'ap-southeast-1';
const LAMBDA = new AWS.Lambda({apiVersion: '2015-03-31'});

LAMBDA.invoke({
	FunctionName: 'edupass',
	Payload: JSON.stringify({
		user: {
			logged_in: true,
			session_id: COOKIE.get('sessid'),
			username: COOKIE.get('username')
		},
		request: {
			type: 'settings_get'
		}
	})
}, (err, data) => {
	if (err) {
		alert('An error occured, see console for details');
		console.error(err);
	}
	else {
		const RESPONSE = JSON.parse(data.Payload);
		if (RESPONSE.theme == 'light' && set) document.head.removeChild(LINK);
		if (RESPONSE.theme != 'light') {
			COOKIE.set('theme', RESPONSE.theme, 7776000);
			LINK.href = `../themes/${window.location.href.split('/').slice(-2)[0]}/${RESPONSE.theme}_theme.css`;
			document.head.appendChild(LINK);
		}
	}
});