import json
import os
import re
from datetime import datetime
from dotenv import load_dotenv

load_dotenv() # Load variables from .env file

from scraper import fetch_latest_news, extract_article_content
from ai_writer import generate_blog_post

HISTORY_FILE = "history.json"
BLOG_POSTS_DIR = "../frontend/src/content/blog"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(history, f, indent=4)

def slugify(text):
    text = text.lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')

def main():
    print("Iniciando proceso automático de blog...")
    history = load_history()
    
    articles = fetch_latest_news()
    
    if not articles:
        print("No se encontraron artículos en el RSS.")
        return
        
    for article in articles:
        if article["link"] in history:
            print(f"Saltando artículo ya procesado: {article['title']}")
            continue
            
        print(f"Procesando nuevo artículo: {article['title']}")
        
        # 1. Extraer contenido de la URL
        content = extract_article_content(article["link"])
        if not content:
            print("Advertencia: No se pudo extraer contenido. Usando solo el título.")
            content = "Contenido no disponible para extracción automática."
            
        # 2. Usar IA para generar el post
        generated_data = generate_blog_post(article["title"], content)
        if not generated_data:
            print("Fallo la generación de IA. Saltando...")
            continue
            
        # 3. Guardar en el frontend (Astro format)
        slug = slugify(generated_data["title"])
        today = datetime.now().strftime("%b %d %Y")
        
        markdown_content = f"""---
title: '{generated_data["title"].replace("'", "''")}'
description: '{generated_data["description"].replace("'", "''")}'
pubDate: '{today}'
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
        history.append(article["link"])
        save_history(history)
        
        # Solo procesamos uno a la vez en esta prueba para no agotar la API rápidamente
        break

    print("Proceso finalizado.")

if __name__ == "__main__":
    main()
