import feedparser
from bs4 import BeautifulSoup
import requests

RSS_FEEDS = [
    # Noticias de IA en Argentina
    "https://news.google.com/rss/search?q=Inteligencia+Artificial+Argentina&hl=es-419&gl=AR&ceid=AR:es-419",
    # Noticias de IA en el mundo (en español)
    "https://news.google.com/rss/search?q=Inteligencia+Artificial&hl=es-419&gl=AR&ceid=AR:es-419",
    # Noticias globales de AI en inglés (más variedad)
    "https://news.google.com/rss/search?q=artificial+intelligence+breakthrough&hl=en-US&gl=US&ceid=US:en",
]

def fetch_latest_news():
    """Fetches the latest news from multiple RSS feeds for variety."""
    print("Buscando noticias en Google News (Argentina + Mundo)...")
    
    articles = []
    seen_links = set()
    
    for rss_url in RSS_FEEDS:
        feed = feedparser.parse(rss_url)
        for entry in feed.entries[:3]:  # Top 3 de cada feed
            if entry.link not in seen_links:
                seen_links.add(entry.link)
                articles.append({
                    "title": entry.title,
                    "link": entry.link,
                    "published": entry.published,
                })
    
    print(f"Total de noticias únicas encontradas: {len(articles)}")
    return articles

def extract_article_content(url):
    """Attempts to extract the main text content from a URL."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, timeout=10, headers=headers)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        content = "\n".join([p.get_text() for p in paragraphs if len(p.get_text()) > 20])
        return content
    except Exception as e:
        print(f"Error extrayendo {url}: {e}")
        return ""
