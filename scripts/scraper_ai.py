import requests
import json
import os

# Usa la tua API KEY da variabile d'ambiente per sicurezza
API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent?key={API_KEY}"

HEADERS = {
    "Content-Type": "application/json"
}

# Categorie da analizzare
CATEGORIES = {
    "Business": "https://1lib.sk/category/5/Business--Economics/s/",
    "Psychology": "https://1lib.sk/category/29/Psychology/s/",
    "SelfHelp": "https://1lib.sk/category/35/Self-Help-Relationships--Lifestyle/s/",
    "Society": "https://1lib.sk/category/36/Society-Politics--Philosophy/s/"
}

def estrai_html(url):
    try:
        res = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if res.status_code == 200:
            return res.text[:15000]  # Limita la dimensione per Gemini
        else:
            return None
    except Exception as e:
        print("Errore:", e)
        return None

def usa_gemini(prompt):
    data = {
        "contents": [{
            "parts": [{"text": prompt}]
        }]
    }
    response = requests.post(GEMINI_URL, headers=HEADERS, data=json.dumps(data))
    res_json = response.json()
    try:
        return res_json["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        print("Errore nella risposta Gemini:", e)
        print(res_json)
        return None

def main():
    all_html = "<html><head><title>Catalogo AI</title></head><body><h1>Catalogo creato con Gemini AI</h1>"

    for category, url in CATEGORIES.items():
        print(f"📥 Analizzo: {category}")
        html = estrai_html(url)
        if not html:
            continue

        prompt = f"""Sei un assistente AI. Analizza questo HTML di una pagina di libri e restituisci una lista dei libri trovati in HTML.
Ogni libro deve includere titolo, immagine di copertina (URL), categoria '{category}' e link al dettaglio.  
Rispondi solo con codice HTML (senza spiegazioni).

Contenuto HTML:
{html}"""

        result = usa_gemini(prompt)
        if result:
            all_html += f"<h2>{category}</h2>" + result
        else:
            all_html += f"<p>Nessun risultato trovato per {category}</p>"

    all_html += "</body></html>"

    with open("index.html", "w", encoding="utf-8") as f:
        f.write(all_html)

    print("✅ index.html creato con Gemini")

if __name__ == "__main__":
    main()
