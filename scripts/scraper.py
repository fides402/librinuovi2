import requests
from bs4 import BeautifulSoup
import datetime
import time

BASE_URLS = {
    "Business--Economics": "https://1lib.sk/category/5/Business--Economics/s/",
    "Psychology": "http://1lib.sk/category/29/Psychology/s/",
    "Self-Help-Relationships--Lifestyle": "https://1lib.sk/category/35/Self-Help-Relationships--Lifestyle/s/",
    "Society-Politics--Philosophy": "https://1lib.sk/category/36/Society-Politics--Philosophy/s/"
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

def get_books_from_category(name, base_url):
    books = []
    page = 1

    while True:
        params = {
            "yearFrom": 2025,
            "languages[]": ["italian", "english"],
            "order": "date",
            "page": page
        }

        print(f"[{name}] Scaricando pagina {page}...")
        res = requests.get(base_url, params=params, headers=HEADERS)
        if res.status_code != 200:
            print(f"Errore nella richiesta: {res.status_code}")
            break

        soup = BeautifulSoup(res.text, "html.parser")
        book_boxes = soup.select(".resItemBox")

        if not book_boxes:
            break

        for box in book_boxes:
            title_tag = box.select_one(".bookTitle")
            link_tag = box.select_one("a")
            img_tag = box.select_one("img")

            if not title_tag or not link_tag or not img_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = "https://1lib.sk" + link_tag.get("href")
            image = img_tag.get("data-src") or img_tag.get("src")

            books.append({
                "title": title,
                "link": link,
                "image": image,
                "category": name
            })

        page += 1
        time.sleep(1)  # Evita di farsi bloccare

    print(f"[{name}] Totale libri trovati: {len(books)}")
    return books

def generate_html(books):
    html = f"<html><head><title>Catalogo Libri - {datetime.date.today()}</title></head><body>"
    html += f"<h1>Catalogo aggiornato: {datetime.date.today()}</h1>"

    if not books:
        html += "<p>Nessun libro trovato oggi. Riprova domani!</p>"

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
    for name, url in BASE_URLS.items():
        books = get_books_from_category(name, url)
        all_books.extend(books)

    html = generate_html(all_books)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n✅ Totale libri raccolti: {len(all_books)}")

if __name__ == "__main__":
    main()
