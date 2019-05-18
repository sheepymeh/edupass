// This user is limited to the EduPass Lambda function, which handles authorization within the function
AWS.config.accessKeyId = 'AKIAQF4IUI6AIH5HNSOF';
AWS.config.secretAccessKey = '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';
AWS.config.region = 'ap-southeast-1';
const LAMBDA = new AWS.Lambda({apiVersion: '2015-03-31'});

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

if (!COOKIE.get('sessid') || !COOKIE.get('username')) window.location = 'http://sheepymeh.github.io/edupass/login.html';
