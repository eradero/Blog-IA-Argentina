import os
import re
import requests
from ai_writer import verify_image_relevance
from scraper import search_unsplash_image

BLOG_POSTS_DIR = "../frontend/src/content/blog"
PUBLIC_IMAGES_DIR = "../frontend/public/images"
BAD_PLACEHOLDER = "https://images.unsplash.com/photo-1675271591211-126ad94e495d"

def get_latest_posts(n=5):
    if not os.path.exists(BLOG_POSTS_DIR):
        return []
    
    files = [f for f in os.listdir(BLOG_POSTS_DIR) if f.endswith(".md")]
    # Sort by modification time (latest first)
    files.sort(key=lambda x: os.path.getmtime(os.path.join(BLOG_POSTS_DIR, x)), reverse=True)
    return files[:n]

def verify_and_fix_post(filename):
    file_path = os.path.join(BLOG_POSTS_DIR, filename)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract frontmatter
    title_match = re.search(r"title: '(.*?)'", content)
    image_match = re.search(r"heroImage: '(.*?)'", content)
    
    if not title_match or not image_match:
        return
    
    title = title_match.group(1)
    image_url = image_match.group(1)
    
    print(f"Verificando: {title}")
    
    needs_fix = False
    if BAD_PLACEHOLDER in image_url:
        print(f"  -> Placeholder detectado.")
        needs_fix = True
    elif not image_url.startswith("http") and not os.path.exists(os.path.join("../frontend/public", image_url.lstrip("/"))):
        print(f"  -> Imagen local no encontrada: {image_url}")
        needs_fix = True
    else:
        # Use Gemini to verify relevance (only if it's not a known bad placeholder)
        is_relevant = verify_image_relevance(image_url, title)
        if not is_relevant:
            print(f"  -> Imagen marcada como irrelevante por Gemini.")
            needs_fix = True

    if needs_fix:
        print(f"  -> Buscando nueva imagen para: {title}")
        new_image_url = search_unsplash_image(title)
        if new_image_url:
            print(f"  -> Nueva imagen encontrada: {new_image_url}")
            new_content = content.replace(f"heroImage: '{image_url}'", f"heroImage: '{new_image_url}'")
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            print(f"  -> Post actualizado: {filename}")
        else:
            print(f"  -> No se encontró una mejor imagen en Unsplash.")

def main():
    print("Iniciando verificación diaria de imágenes...")
    latest_posts = get_latest_posts(10) # Revisar las últimas 10
    for post in latest_posts:
        verify_and_fix_post(post)
    print("Verificación finalizada.")

if __name__ == "__main__":
    main()
