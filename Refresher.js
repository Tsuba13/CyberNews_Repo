let titles = [];
let text = [];
let currentIndex = 0;

fetch('Articles.json')
	.then(response => response.json())
	.then(data => {
		titles = data.Titles;
		text = data.Text;
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

	const article = document.createElement('article');
	const h3 = document.createElement('h3');
	const p = document.createElement('p');
	const divider = document.createElement('hr');

	h3.textContent = titles[currentIndex];
	p.textContent = text[currentIndex];

	article.appendChild(h3);
	article.appendChild(p);
	container.appendChild(article);
	container.appendChild(divider);

	currentIndex++;
}
