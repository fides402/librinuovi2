import requests
from bs4 import BeautifulSoup
import json
import time
import random
import re
import os
from urllib.parse import urljoin

# Configurazioni e costanti
BASE_URL = "https://1lib.sk"
CATEGORIES = {
    "business": "/category/5/Business--Economics/s/?yearFrom=2025&languages%5B%5D=italian&languages%5B%5D=english&order=date",
    "psychology": "/category/29/Psychology/s/?yearFrom=2025&languages%5B%5D=italian&languages%5B%5D=english&order=date",
    "self_help": "/category/35/Self-Help-Relationships--Lifestyle/s/?yearFrom=2025&languages%5B%5D=italian&languages%5B%5D=english&order=date",
    "society": "/category/36/Society-Politics--Philosophy/s/?yearFrom=2025&languages%5B%5D=italian&languages%5B%5D=english&order=date"
}

# Headers per simulare un browser
HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Referer': 'https://1lib.sk/',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
}

def fetch_page(url):
    """Recupera il contenuto HTML di una pagina."""
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Errore nel recupero della pagina {url}: {e}")
        return None

def parse_books(html):
    """Estrae i dati dei libri da una pagina HTML."""
    books = []
    soup = BeautifulSoup(html, 'html.parser')
    
    # Utilizza i selettori CSS basati sugli screenshot
    book_elements = soup.select("div.resItemBox")
    
    for book_element in book_elements:
        book = {}
        
        # Titolo e link
        title_elem = book_element.select_one("h3.arts__body__title a")
        if title_elem:
            book['title'] = title_elem.get_text(strip=True)
            book['link'] = urljoin(BASE_URL, title_elem.get('href', ''))
        else:
            continue  # Salta questo libro se non ha un titolo
            
        # Immagine di copertina
        cover_img = book_element.select_one("img.cover")
        book['cover_url'] = cover_img.get('src') if cover_img else None
        
        # Casa editrice
        publisher_elem = book_element.select_one("div:not(.authors)")
        book['publisher'] = publisher_elem.get_text(strip=True) if publisher_elem else None
        
        # Autore
        author_elem = book_element.select_one("div.authors")
        book['author'] = author_elem.get_text(strip=True) if author_elem else None
        
        # Informazioni sul libro (anno, lingua, formato, dimensione)
        property_values = book_element.select("div.property_value")
        for prop in property_values:
            text = prop.get_text(strip=True)
            if "Year:" in text:
                book['year'] = text.replace("Year:", "").strip()
            elif "Language:" in text:
                book['language'] = text.replace("Language:", "").strip()
            elif "File:" in text:
                file_info = text.replace("File:", "").strip()
                
                # Estrai formato (PDF, EPUB, ecc.)
                format_match = re.search(r'(PDF|EPUB|MOBI|DJVU|FB2|AZW3|AZW|TXT)', file_info, re.IGNORECASE)
                book['format'] = format_match.group(0) if format_match else None
                
                # Estrai dimensione (MB, KB)
                size_match = re.search(r'\d+(\.\d+)?\s*(MB|KB)', file_info, re.IGNORECASE)
                book['size'] = size_match.group(0) if size_match else None
        
        # Valutazione
        rating_elem = book_element.select_one("div.book-rating")
        if rating_elem:
            rating_text = rating_elem.get_text(strip=True)
            rating_match = re.search(r'(\d+(\.\d+)?)\s*/\s*(\d+(\.\d+)?)', rating_text)
            book['rating'] = rating_match.group(0) if rating_match else None
        else:
            book['rating'] = None
            
        books.append(book)
    
    # Se non abbiamo trovato libri con il selettore normale, prova un approccio alternativo
    if not books:
        # Analizza le righe della tabella
        rows = soup.select("tr")
        for row in rows:
            # Verifica se è una riga di libro (ha almeno un titolo)
            if not row.select_one("h3"):
                continue
                
            book = {}
            
            # Titolo e link
            title_elem = row.select_one("h3 a")
            if title_elem:
                book['title'] = title_elem.get_text(strip=True)
                book['link'] = urljoin(BASE_URL, title_elem.get('href', ''))
            else:
                continue
            
            # Immagine di copertina
            cover_img = row.select_one("img")
            book['cover_url'] = cover_img.get('src') if cover_img else None
            
            # Autore
            author_elem = row.select_one(".authors")
            book['author'] = author_elem.get_text(strip=True) if author_elem else None
            
            # Estrai anno, lingua, formato, dimensione
            for span in row.select("div"):
                text = span.get_text(strip=True)
                if "Year:" in text:
                    book['year'] = text.replace("Year:", "").strip()
                elif "Language:" in text:
                    book['language'] = text.replace("Language:", "").strip()
                elif "File:" in text:
                    file_info = text.replace("File:", "").strip()
                    
                    # Estrai formato (PDF, EPUB, ecc.)
                    format_match = re.search(r'(PDF|EPUB|MOBI|DJVU|FB2|AZW3|AZW|TXT)', file_info, re.IGNORECASE)
                    book['format'] = format_match.group(0) if format_match else None
                    
                    # Estrai dimensione (MB, KB)
                    size_match = re.search(r'\d+(\.\d+)?\s*(MB|KB)', file_info, re.IGNORECASE)
                    book['size'] = size_match.group(0) if size_match else None
            
            # Valutazione
            for div in row.select("div"):
                if "star" in div.get('class', []):
                    book['rating'] = div.get_text(strip=True)
                    break
            else:
                book['rating'] = None
                
            books.append(book)
    
    return books

def get_next_page_url(html, current_url):
    """Determina l'URL della pagina successiva."""
    soup = BeautifulSoup(html, 'html.parser')
    
    # Cerca il link "next page" o simile
    next_link = soup.select_one("a.next_page")
    if next_link and next_link.get('href'):
        return urljoin(BASE_URL, next_link.get('href'))
    
    # Se non troviamo un link specifico, possiamo costruirlo manualmente
    if "page=" in current_url:
        match = re.search(r'page=(\d+)', current_url)
        if match:
            current_page = int(match.group(1))
            next_page = current_page + 1
            return re.sub(r'page=\d+', f'page={next_page}', current_url)
    else:
        # Se non c'è un parametro page, aggiungiamolo
        separator = '&' if '?' in current_url else '?'
        return f"{current_url}{separator}page=2"
    
    return None

def scrape_category(category_url, max_pages=10):
    """Esegue lo scraping di una categoria per un numero massimo di pagine."""
    all_books = []
    current_url = category_url
    page = 1
    
    while page <= max_pages:
        print(f"Scraping pagina {page}: {current_url}")
        html = fetch_page(current_url)
        
        if not html:
            print(f"Non è stato possibile recuperare la pagina {page}. Tentativo fallito.")
            break
        
        books = parse_books(html)
        if not books:
            print(f"Nessun libro trovato nella pagina {page}. Fine dello scraping per questa categoria.")
            break
        
        all_books.extend(books)
        print(f"Trovati {len(books)} libri nella pagina {page}")
        
        # Trova il link alla pagina successiva
        next_url = get_next_page_url(html, current_url)
        if not next_url or next_url == current_url:
            print("Nessuna pagina successiva trovata. Fine dello scraping per questa categoria.")
            break
        
        current_url = next_url
        page += 1
        
        # Pausa per evitare di sovraccaricare il server
        delay = random.uniform(2.0, 5.0)
        print(f"Pausa di {delay:.2f} secondi prima della prossima richiesta...")
        time.sleep(delay)
    
    return all_books

def main():
    """Funzione principale del programma."""
    print("Inizio dello scraping di libri da 1lib.sk...")
    results = {}
    
    for category_name, category_path in CATEGORIES.items():
        print(f"\n{'=' * 50}")
        print(f"Scraping della categoria: {category_name}")
        print(f"{'=' * 50}")
        
        category_url = urljoin(BASE_URL, category_path)
        books = scrape_category(category_url)
        
        # Filtra eventuali duplicati
        unique_books = []
        seen = set()
        
        for book in books:
            if book['title'] not in seen:
                seen.add(book['title'])
                unique_books.append(book)
        
        results[category_name] = unique_books
        
        print(f"Completato lo scraping della categoria {category_name}. "
              f"Raccolti {len(unique_books)} libri unici.")
        
        # Pausa tra categorie diverse
        if category_name != list(CATEGORIES.keys())[-1]:  # Se non è l'ultima categoria
            delay = random.uniform(5.0, 10.0)
            print(f"Pausa di {delay:.2f} secondi prima della categoria successiva...")
            time.sleep(delay)
    
    # Salva i risultati in un file JSON
    output_file = 'libri_1lib.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    total_books = sum(len(books) for books in results.values())
    print(f"\nOperazione completata. Salvati {total_books} libri in totale nel file {output_file}.")

if __name__ == "__main__":
    main()
