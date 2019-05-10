const cookie = {
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
			if (cookie.includes(name)) return cookie.substring(name.length, cookie.length)
		}
		return false;
	},
	delete: name =>
		document.cookie = `${name}=expired;expires=Thu, 01 Jan 1970 00:00:00 GMT;path=/`
}