import requests
from bs4 import BeautifulSoup
import datetime
import time

def get_books_from_page(url, category):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    books = []
    page = 1

    while True:
        print(f"⏳ Scraping pagina {page} di {category}")
        res = requests.get(f"{url}&page={page}", headers=headers)
        if res.status_code != 200:
            print("⚠️ Errore nella richiesta:", res.status_code)
            break

        soup = BeautifulSoup(res.text, "html.parser")
        book_items = soup.select("div.resItemBox")

        if not book_items:
            break  # nessun altro libro = fine delle pagine

        for item in book_items:
            title_tag = item.select_one(".bookTitle")
            link_tag = item.select_one("a[href]")
            img_tag = item.select_one("img")

            if not title_tag or not link_tag or not img_tag:
                continue

            title = title_tag.text.strip()
            link = "https://1lib.sk" + link_tag["href"]
            img = img_tag.get("data-src") or img_tag.get("src")

            books.append({
                "title": title,
                "link": link,
                "image": img,
                "category": category
            })

        page += 1
        time.sleep(1)  # evita blocchi

    return books

def generate_html(books):
    today = datetime.date.today()
    html = f"<html><head><title>Catalogo Libri - {today}</title></head><body>"
    html += f"<h1>Catalogo aggiornato: {today}</h1>"

    if not books:
        html += "<p>Nessun libro trovato.</p>"

    for book in books:
        html += f"""
        <div style="margin-bottom: 30px;">
            <h3>{book['title']}</h3>
            <img src="{book['image']}" alt="{book['title']}" style="max-height: 200px;"><br>
            <strong>Categoria:</strong> {book['category']}<br>
            <a href="{book['link']}" target="_blank">Vai al libro</a>
        </div>
        <hr>
        """

    html += "</body></html>"
    return html

def main():
    categories = {
        "Business & Economics": "https://1lib.sk/category/5/Business--Economics/s/?yearFrom=2025&languages%5B%5D=italian&languages%5B%5D=english&order=date",
        "Psychology": "http://1lib.sk/category/29/Psychology/s/?yearFrom=2025&languages%5B%5D=italian&languages%5B%5D=english&order=date",
        "Self-Help, Relationships & Lifestyle": "https://1lib.sk/category/35/Self-Help-Relationships--Lifestyle/s/?yearFrom=2025&languages%5B%5D=italian&languages%5B%5D=english&order=date",
        "Society, Politics & Philosophy": "https://1lib.sk/category/36/Society-Politics--Philosophy/s/?yearFrom=2025&languages%5B%5D=italian&languages%5B%5D=english&order=date"
    }

    all_books = []
    for category, url in categories.items():
        books = get_books_from_page(url, category)
        all_books.extend(books)

    html = generate_html(all_books)
    with open("index.html", "w", encoding="utf-8") as f:
        f.write(html)

    print(f"✅ Scraping completato: {len(all_books)} libri trovati.")

if __name__ == "__main__":
    main()
