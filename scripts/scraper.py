import requests
from bs4 import BeautifulSoup
import datetime

BASE_URLS = [
    "https://1lib.sk/category/5/Business--Economics/s/",
    "http://1lib.sk/category/29/Psychology/s/",
    "https://1lib.sk/category/35/Self-Help-Relationships--Lifestyle/s/",
    "https://1lib.sk/category/36/Society-Politics--Philosophy/s/"
]

PARAMS = {
    "yearFrom": 2025,
    "languages[]": ["italian", "english"],
    "order": "date",
    "page": 1  # inizializzato ma verrà sovrascritto in loop
}

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_books_from_category(base_url):
    page = 1
    all_books = []
    category = base_url.split("/")[4]

    while True:
        print(f"Scraping pagina {page} di {category}...")
        PARAMS["page"] = page
        response = requests.get(base_url, params=PARAMS, headers=HEADERS)

        if response.status_code != 200:
            print(f"Errore nella richiesta: {response.status_code}")
            break

        soup = BeautifulSoup(response.text, 'html.parser')
        book_divs = soup.select('.resItemBox')
        if not book_divs:
            break  # Nessun libro = fine della lista

        for book_div in book_divs:
            title = book_div.select_one('.bookTitle').text.strip()
            link = 'https://1lib.sk' + book_div.select_one('a')['href']
            img_tag = book_div.select_one('img')
            image = img_tag.get('data-src') or img_tag.get('src')

            all_books.append({
                'title': title,
                'link': link,
                'image': image,
                'category': category
            })

        page += 1

    return all_books

def generate_html(books):
    html = f"<html><head><title>Catalogo Libri - {datetime.date.today()}</title></head><body>"
    html += f"<h1>Catalogo aggiornato: {datetime.date.today()}</h1>"
    for book in books:
        html += f"""
        <div>
            <h3>{book['title']}</h3>
            <img src="{book['image']}" alt="{book['title']}" style="height:200px;"><br>
            <strong>Categoria:</strong> {book['category']}<br>
            <a href="{book['link']}">Vai al libro</a>
            <hr>
        </div>
        """
    html += "</body></html>"
    return html

def main():
    all_books = []
    for base_url in BASE_URLS:
        books = get_books_from_category(base_url)
        all_books.extend(books)

    html = generate_html(all_books)

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

if __name__ == "__main__":
    main()
