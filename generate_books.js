<!DOCTYPE html>
<html lang="it">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>RecentBooks - Libri ultimi 7 giorni</title>
  <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
  <link href="https://cdn.jsdelivr.net/npm/@fortawesome/fontawesome-free@6.0.0/css/all.min.css" rel="stylesheet">
  <style>
    .loading { display:inline-block; width:50px; height:50px; border:3px solid rgba(79,70,229,0.3); border-radius:50%; border-top-color:#4f46e5; animation:spin 1s linear infinite; }
    @keyframes spin { to { transform:rotate(360deg); } }
    .book-card { transition: transform 0.3s ease; }
    .book-card:hover { transform: translateY(-5px); box-shadow:0 10px 20px rgba(0,0,0,0.1); }
    .book-cover { height:180px; object-fit:contain; }
  </style>
</head>
<body class="min-h-screen bg-gray-50">
  <div class="container mx-auto px-4 py-8">
    <header class="text-center mb-8">
      <h1 class="text-4xl font-bold text-indigo-700 mb-2">RecentBooks</h1>
      <p class="text-lg text-gray-600">Libri pubblicati nell'ultima settimana in USA e Italia<br>Categorie: Business, Psicologia, Self-Help, Società, Filosofia</p>
    </header>
    <div class="text-center mb-6">
      <button id="searchBtn" class="inline-flex items-center bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-3 px-6 rounded-full">
        <i class="fas fa-search mr-2"></i> Trova Libri
      </button>
    </div>
    <div id="loadingIndicator" class="hidden flex justify-center my-8"><div class="loading"></div></div>
    <div id="resultsSection" class="hidden">
      <h2 class="text-2xl font-semibold text-gray-800 mb-4 text-center">Risultati</h2>
      <div id="resultsContainer" class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6"></div>
    </div>
  </div>
  <script>
    const apiKey = 'AIzaSyBVtXwnVXilsNqLx6of2HG2jiYwAWs-btg';
    const categories = ['Business','Psychology','Self-Help','Social Science','Philosophy'];
    const languages = ['en','it'];
    const oneWeekAgo = Date.now() - 7*24*60*60*1000;
    const maxResults = 40;

    document.getElementById('searchBtn').addEventListener('click', async () => {
      const btn = document.getElementById('searchBtn');
      const loader = document.getElementById('loadingIndicator');
      const section = document.getElementById('resultsSection');
      const container = document.getElementById('resultsContainer');
      btn.disabled = true;
      loader.classList.remove('hidden');
      section.classList.add('hidden');
      container.innerHTML = '';

      let all = [];
      for (const lang of languages) {
        for (const cat of categories) {
          const url = `https://www.googleapis.com/books/v1/volumes?q=subject:${encodeURIComponent(cat)}&orderBy=newest&maxResults=${maxResults}&langRestrict=${lang}&key=${apiKey}`;
          try {
            const res = await fetch(url);
            const data = await res.json();
            if (!data.items) continue;
            data.items.forEach(item => {
              const info = item.volumeInfo;
              const dateStr = info.publishedDate;
              if (!dateStr) return;
              let time;
              if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) time = Date.parse(dateStr);
              else if (/^\d{4}-\d{2}$/.test(dateStr)) time = Date.parse(dateStr + '-01');
              else if (/^\d{4}$/.test(dateStr)) time = Date.parse(dateStr + '-01-01');
              if (!time || time < oneWeekAgo) return;
              all.push({
                title: info.title || 'Sconosciuto',
                author: info.authors ? info.authors.join(', ') : 'Sconosciuto',
                cover: info.imageLinks?.thumbnail?.replace('http:','https:'),
                archiveLink: `https://annas-archive.org/search?q=${encodeURIComponent(info.title)}`
              });
            });
          } catch(e) {
            console.error('Errore fetch', e);
          }
        }
      }
      // dedup
      const seen = new Set();
      all = all.filter(b => {
        const key = b.title + '|' + b.author;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });

      loader.classList.add('hidden');
      btn.disabled = false;

      if (!all.length) {
        container.innerHTML = '<p class="text-center text-gray-500">❌ Nessun libro recente trovato.</p>';
      } else {
        all.forEach(b => {
          const card = document.createElement('div');
          card.className = 'book-card bg-white rounded-lg shadow-md overflow-hidden flex flex-col';
          card.innerHTML = `
            <div class="p-4 bg-gray-50 flex justify-center">
              ${b.cover ? `<img src="${b.cover}" alt="${b.title}" class="book-cover">` : `<i class="fas fa-book fa-5x text-gray-300"></i>`}
            </div>
            <div class="p-4 flex-grow">
              <h3 class="font-bold text-lg text-indigo-700 line-clamp-2">${b.title}</h3>
              <p class="text-gray-700 mt-1">${b.author}</p>
            </div>
            <div class="p-4 pt-2 border-t border-gray-100">
              <a href="${b.archiveLink}" target="_blank" class="block bg-indigo-600 hover:bg-indigo-700 text-white text-center py-2 rounded-md text-sm">
                <i class="fas fa-archive mr-1"></i> Anna's Archive
              </a>
            </div>`;
          container.appendChild(card);
        });
      }
      section.classList.remove('hidden');
    });
  </script>
</body>
</html>
