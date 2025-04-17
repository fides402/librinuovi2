/**
 * Script per generare un file JSON con tutti i libri pubblicati nell'ultima settimana
 * USA + ITA, categorie: Business, Psychology, Self-Help, Social Science, Philosophy
 * Output: books.json nella root del progetto
 * 
 * Usa Node.js >= 18 per fetch globale oppure installa node-fetch.
 * Esegui: `node generate_books.js` e poi deploya books.json.
 */
import { writeFile } from 'fs/promises';

const apiKey = 'AIzaSyBVtXwnVXilsNqLx6of2HG2jiYwAWs-btg';
const categories = ['Business','Psychology','Self-Help','Social Science','Philosophy'];
const locales = ['en','it'];
const maxPerCat = 20;
const oneWeekAgo = Date.now() - 7*24*60*60*1000;

async function fetchBooks() {
  let all = [];
  for (const lang of locales) {
    for (const cat of categories) {
      const url = `https://www.googleapis.com/books/v1/volumes?q=subject:${encodeURIComponent(cat)}&orderBy=newest&maxResults=${maxPerCat}&langRestrict=${lang}&key=${apiKey}`;
      try {
        const res = await fetch(url);
        const data = await res.json();
        if (data.items) {
          data.items.forEach(item => {
            const info = item.volumeInfo;
            const dateStr = info.publishedDate;
            if (!dateStr) return;
            let pubTime;
            if (/^\d{4}-\d{2}-\d{2}$/.test(dateStr)) pubTime = Date.parse(dateStr);
            else if (/^\d{4}-\d{2}$/.test(dateStr)) pubTime = Date.parse(dateStr+'-01');
            else if (/^\d{4}$/.test(dateStr)) pubTime = Date.parse(dateStr+'-01-01');
            if (!pubTime || pubTime < oneWeekAgo) return;
            all.push({
              title: info.title || 'Sconosciuto',
              author: info.authors ? info.authors.join(', ') : 'Sconosciuto',
              cover: info.imageLinks?.thumbnail?.replace('http:', 'https:'),
              archiveLink: `https://annas-archive.org/search?q=${encodeURIComponent(info.title)}`
            });
          });
        }
      } catch (e) {
        console.error(`Errore fetch ${cat} ${lang}:`, e);
      }
    }
  }
  // dedup
  const seen = new Set();
  const unique = all.filter(b => {
    const key = b.title + '|' + b.author;
    if (seen.has(key)) return false;
    seen.add(key);
    return true;
  });
  return unique;
}

(async () => {
  const books = await fetchBooks();
  await writeFile('books.json', JSON.stringify(books, null, 2), 'utf-8');
  console.log(`Generati ${books.length} libri in books.json`);
})();
