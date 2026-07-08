setTimeout(function() {
	var notice = document.getElementById('cookie-notice');
	if (notice) {
		notice.style.opacity = '0';
		setTimeout(function() {
			notice.style.display = 'none';
		}, 500);
	}
}, 4000);
