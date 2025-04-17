/**
 * Script per generare books.json scrappando BookFinder.com
 * per ultime uscite (ordinamento per data) USA (lang=en) e Italia (lang=it)
 * Categorie: Business, Psychology, Self-Help, Social Science, Philosophy
 * Output: books.json
 *
 * Usa Node.js e dipendenze: cheerio, node-fetch
 * Installa: npm install node-fetch@2 cheerio
 * Esegui: node generate_books.js
 */
const fs = require('fs');
const fetch = require('node-fetch');
const cheerio = require('cheerio');

const categories = ['Business','Psychology','Self-Help','Social Science','Philosophy'];
const locales = ['en','it'];
const maxResults = 10;

function buildUrl(category, lang) {
  const q = encodeURIComponent(category);
  return `https://www.bookfinder.com/search/?q=${q}&lang=${lang}&sort=pubdate&st=sh&ac=qr`;
}

async function scrapeCategory(category, lang) {
  const url = buildUrl(category, lang);
  const res = await fetch(url, { headers: { 'User-Agent': 'Mozilla/5.0' } });
  const text = await res.text();
  const $ = cheerio.load(text);
  const results = [];
  $('.bookresult').slice(0, maxResults).each((i, el) => {
    const title = $(el).find('.booktitle a').text().trim();
    const author = $(el).find('.bookauthor').text().replace(/^by\s+/i, '').trim();
    const cover = $(el).find('.bookcover img').attr('src');
    const link = 'https://www.bookfinder.com' + $(el).find('.booktitle a').attr('href');
    if (title) {
      results.push({ title, author, cover, link, archiveLink: `https://annas-archive.org/search?q=${encodeURIComponent(title)}` });
    }
  });
  return results;
}

(async () => {
  let all = [];
  for (const lang of locales) {
    for (const cat of categories) {
      try {
        const books = await scrapeCategory(cat, lang);
        all.push(...books);
      } catch (e) {
        console.error(`Errore scraping ${cat} ${lang}:`, e);
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
  fs.writeFileSync('books.json', JSON.stringify(unique, null, 2));
  console.log(`Generati ${unique.length} libri da BookFinder.com in books.json`);
})();
