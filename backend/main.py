import json
import os
import re
import urllib.parse
import requests
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file

from scraper import fetch_latest_news, extract_article_content, search_unsplash_image
from ai_writer import generate_blog_post, verify_image_relevance

HISTORY_FILE = "history.json"
BLOG_POSTS_DIR = "../frontend/src/content/blog"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            data = json.load(f)
        return [item if isinstance(item, dict) else {"link": item, "title": ""} for item in data]
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def is_duplicate(title, history):
    title_words = set(re.findall(r"\w+", title.lower()))
    if len(title_words) < 4: return False
    
    # Ignorar palabras comunes
    stop_words = {'de', 'la', 'en', 'el', 'un', 'una', 'con', 'por', 'para', 'que', 'y', 'los', 'las', 'sobre', 'del', 'con', 'para'}
    title_words = {w for w in title_words if w not in stop_words}
    
    # 1. Verificar contra archivos en el disco (por si history.json no está al día)
    existing_titles = []
    if os.path.exists(BLOG_POSTS_DIR):
        for f in os.listdir(BLOG_POSTS_DIR):
            if f.endswith(".md"):
                existing_titles.append(f.replace("-", " ").replace(".md", ""))
    
    # 2. Combinar historial y archivos físicos
    check_list = history + [{"title": t} for t in existing_titles]
    
    for item in check_list:
        if isinstance(item, dict) and item.get("title"):
            h_words = set(re.findall(r"\w+", item["title"].lower()))
            h_words = {w for w in h_words if w not in stop_words}
            if not h_words: continue
            
            intersection = title_words.intersection(h_words)
            if not title_words: continue
            overlap = len(intersection) / len(title_words)
            
            if overlap > 0.3: # Si el 50% de las palabras del título nuevo ya existen en uno viejo
                return True
    return False

def main():
    print("Iniciando proceso automático de blog...")
    history = load_history()
    
    articles = fetch_latest_news()
    
    if not articles:
        print("No se encontraron artículos en el RSS.")
        return
        
    for article in articles:
        if any(isinstance(h, dict) and h.get("link") == article["link"] for h in history) or is_duplicate(article["title"], history):
            print(f"Saltando artículo ya procesado: {article['title']}")
            continue
            
        print(f"Procesando nuevo artículo: {article['title']}")
        
        # 1. Extraer contenido de la URL
        content, image_url = extract_article_content(article["link"])
        if not content:
            print("Advertencia: No se pudo extraer contenido. Usando solo el título.")
            content = "Contenido no disponible para extracción automática."
            
        # 2. Usar IA para generar el post
        generated_data = generate_blog_post(article["title"], content)
        if not generated_data:
            print("Fallo la generación de IA. Saltando...")
            continue
            
        # 3. Determinar imagen (1. Real de la noticia, 2. Internet, 3. IA)
        slug = slugify(generated_data["title"])
        
        # Capa 1: Imagen de la noticia
        final_image_url = image_url
        
        # Capa 2: Buscar en Unsplash (Imágenes reales y de alta calidad)
        if not final_image_url:
            print(f"Buscando imagen real en Unsplash para: {generated_data['title']}")
            final_image_url = search_unsplash_image(generated_data["title"])
            
        # Capa 3: Buscar en internet general (Bing) como último recurso
        if not final_image_url:
            print(f"No se encontró en Unsplash. Buscando en internet general para: {article['title']}")
            from scraper import search_internet_image
            final_image_url = search_internet_image(article["title"])
            
        # Capa 4: Si todo falla, NO USAR IA. Usar una imagen de tecnología genérica PERO REAL de Unsplash (no el placeholder de siempre)
        if not final_image_url:
            print(f"Todo falló. Usando imagen de tecnología real como respaldo.")
            final_image_url = "https://images.unsplash.com/photo-1518770660439-4636190af475?q=80&w=1024" # Circuito electrónico real
            
        image_path = f"/images/{slug}.jpg"
        full_image_path = os.path.join("../frontend/public", f"images/{slug}.jpg")
        
        try:
            print(f"Descargando imagen final: {final_image_url}")
            os.makedirs(os.path.dirname(full_image_path), exist_ok=True)
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
            img_response = requests.get(final_image_url, timeout=30, headers=headers)
            
            if img_response.status_code == 200:
                with open(full_image_path, "wb") as f:
                    f.write(img_response.content)
            else:
                print(f"Fallo descarga. Usando link directo a Unsplash.")
                image_path = "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=1024"
        except Exception as e:
            print(f"Error gestionando imagen: {e}")
            image_path = "https://images.unsplash.com/photo-1485827404703-89b55fcc595e?q=80&w=1024"
            
        # 4. Guardar en el frontend (Astro format)
        today = datetime.now().strftime("%b %d %Y")
        
        markdown_content = f"""---
title: '{generated_data["title"].replace("'", "''")}'
description: '{generated_data["description"].replace("'", "''")}'
pubDate: '{today}'
heroImage: '{image_path}'
affiliateLink: '{generated_data["affiliateLink"]}'
---

{generated_data["content"]}
"""
        
        # Make sure directory exists
        os.makedirs(BLOG_POSTS_DIR, exist_ok=True)
        file_path = os.path.join(BLOG_POSTS_DIR, f"{slug}.md")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(markdown_content)
            
        print(f"Guardado exitosamente: {file_path}")
        
        # 4. Actualizar historial
        history.append({"link": article["link"], "title": article["title"]})
        save_history(history)
        

    print("Proceso finalizado.")

if __name__ == "__main__":
    main()
