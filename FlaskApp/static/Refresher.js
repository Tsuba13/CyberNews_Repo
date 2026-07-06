const RSS_URL = 'https://www.bleepingcomputer.com/feed/';
const API_URL = `https://api.rss2json.com/v1/api.json?rss_url=${encodeURIComponent(RSS_URL)}`;

const refreshButton = document.getElementById('RefreshButton');
const container = document.getElementById('HeadlinesContainer');

refreshButton?.addEventListener('click', fetchLatestNews);

function fetchLatestNews() {
  fetch(API_URL)
    .then(response => response.json())
    .then(data => {
      container.innerHTML = '';
      
      data.items.slice(0, 5).forEach(item => {
        appendArticle(item.title, item.description, item.link, item.pubDate);
      });
    })
    .catch(error => {
      console.error('Failed to fetch:', error);
      container.innerHTML = '<p style="color:red;">Could not load news. Try again later.</p>';
    });
}

function appendArticle(title, description, link, date) {
  const article = document.createElement('article');
  const h3 = document.createElement('h3');
  const p = document.createElement('p');
  const meta = document.createElement('small');
  const a = document.createElement('a');
  
  h3.textContent = title;
  p.textContent = description;
  meta.textContent = new Date(date).toLocaleDateString();
  a.href = link;
  a.textContent = 'Read full story →';
  a.target = '_blank';
  
  article.appendChild(h3);
  article.appendChild(meta);
  article.appendChild(p);
  article.appendChild(a);
  container.appendChild(article);
}
