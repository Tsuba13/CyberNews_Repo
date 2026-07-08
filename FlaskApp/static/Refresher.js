let titles = [];
let text = [];
let date = [];
let currentIndex = 0;

fetch('/static/Articles.json')
	.then(response => {
	    	if (!response.ok) {
	    		throw new Error('Network response was not ok.');
	    	}
	    	return response.json();
	    })
	.then(data => {
		titles = data.Titles;
		text = data.Text;
		date = data.Published;
	});

const refreshButton = document.getElementById('RefreshButton');
const container = document.getElementById('HeadlinesContainer');

refreshButton?.addEventListener('click', appendArticles);

function appendArticles() {
	if (currentIndex >= titles.length) {
		if (!document.getElementById('UpToDateMsg')) {
			const statusMsg = document.createElement('h3');
			statusMsg.id = 'UpToDateMsg';
			statusMsg.textContent = "No more articles to show. You're all up to date!";
			container.appendChild(statusMsg);
		}
		return;
	}

	const articleElement = document.createElement('article');
	const titleElement = document.createElement('h3');
	const textElement = document.createElement('p');
	const dateElement = document.createElement('small');
	const divider = document.createElement('hr');

	titleElement.textContent = titles[currentIndex];
	textElement.textContent = text[currentIndex];
	dateElement.textContent = `Published on: ${date[currentIndex]}`;

	articleElement.appendChild(titleElement);
	articleElement.appendChild(textElement);
	articleElement.appendChild(dateElement);
	
	container.appendChild(articleElement);
	container.appendChild(divider);

	currentIndex++;
}
