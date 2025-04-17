import requests
from bs4 import BeautifulSoup
import datetime
import time

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

BASE_URLS = {
    "Business & Economics": "https://1lib.sk/category/5/Business--Economics/s/",
    "Psychology": "http://1lib.sk/category/29/Psychology/s/",
    "Self-Help, Relationships & Lifestyle": "https://1lib.sk/category/35/Self-Help-Relationships--Lifestyle/s/",
    "Society, Politics & Philosophy": "https://1lib.sk/category/36/Society-Politics--Philosophy/s/"
}

PARAMS = {
    "yearFrom": 2025,
    "languages[]": ["italian", "english"],
    "order": "date",
    "page": 1
}

def get_books_from_category(url, category):
    books = []
    page = 1

    while True:
        print(f"🔄 {category} - Pagina {page}")
        PARAMS["page"] = page
        res = requests.get(url, params=PARAMS, headers=HEADERS)

        if res.status_code != 200:
            print(f"⚠️ Errore HTTP: {res.status_code}")
            break

        soup = BeautifulSoup(res.text, "html.parser")
        book_blocks = soup.select('div[slot="title"]')

        if not book_blocks:
            break

        for title_div in book_blocks:
            title = title_div.text.strip()
            a_tag = title_div.find_parent().find("a", href=True)
            if not a_tag:
                continue
            link = "https://1lib.sk" + a_tag["href"]

            books.append({
                "title": title,
                "link": link,
                "category": category
            })

        page += 1
        time.sleep(1)

    print(f"✅ {category}: {len(books)} libri trovati")
    return books

def generate_html(books):
    today = datetime.date.today()
    html = f"<html><head><title>Catalogo Libri - {today}</title></head><body>"
    html += f"<h1>Catalogo aggiornato: {today}</h1>"

    if not books:
        html += "<p>Nessun libro trovato.</p>"

    for book in books:
        html += f"""
        <div style="margin-bottom: 20px;">
            <h3>{book['title']}</h3>
            <strong>Categoria:</strong> {book['category']}<br>
            <a href="{book['link']}" target="_blank">Vai al libro</a>
        </div>
        <hr>
        """

    html += "</body></html>"
    return html

def main():
    all_books = []
    for category, url in BASE_URLS.items():
        books = get_books_from_category(url, category)
        all_books.extend(books)

    html = generate_html(all_books)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n🔚 Totale libri raccolti: {len(all_books)}")

if __name__ == "__main__":
    main()
