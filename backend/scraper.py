import feedparser
from bs4 import BeautifulSoup
import requests
import urllib.parse
import json
import os
from dotenv import load_dotenv

load_dotenv()

RSS_FEEDS = [
        "https://news.google.com/rss/search?q=Inteligencia+Artificial+Argentina&hl=es-419&gl=AR&ceid=AR:es-419",
        "https://news.google.com/rss/search?q=Inteligencia+Artificial&hl=es-419&gl=AR&ceid=AR:es-419",
        "https://news.google.com/rss/search?q=artificial+intelligence+breakthrough&hl=en-US&gl=US&ceid=US:en"
]

def search_unsplash_image(query):
        """Busca una imagen real en Unsplash basada en el query."""
        access_key = os.getenv("UNSPLASH_ACCESS_KEY")
        if not access_key:
                    return None
                url = f"https://api.unsplash.com/search/photos?query={query}&per_page=1&client_id={access_key}"
    try:
                response = requests.get(url)
                if response.status_code == 200:
                                data = response.json()
                                if data['results']:
                                                    return data['results'][0]['urls']['regular']
    except Exception as e:
        print(f"Error: {e}")
    return None

def fetch_latest_news():
        articles = []
    seen_links = set()
    for rss_url in RSS_FEEDS:
                feed = feedparser.parse(rss_url)
                for entry in feed.entries[:10]:
                                if entry.link not in seen_links:
                                                    articles.append({
                                                                            "title": entry.title,
                                                                            "link": entry.link,
                                                                            "published": entry.published,
                                                    })
                                                    seen_links.add(entry.link)
                                        return articles
                    
