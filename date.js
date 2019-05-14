function generateDateString(date) {
	const DIFF = date - new Date();
	return Math.floor(DIFF / 86400000);
}