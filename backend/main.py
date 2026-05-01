import os
import json
import time
from dotenv import load_dotenv
from scraper import fetch_latest_news, search_unsplash_image
from ai_writer import generate_blog_post

load_dotenv()

HISTORY_FILE = "backend/history.json"

def load_history():
        if os.path.exists(HISTORY_FILE):
                    with open(HISTORY_FILE, "r") as f:
                                    return json.load(f)
                            return []

    def save_history(history):
            with open(HISTORY_FILE, "w") as f:
                        json.dump(history, f, indent=4)

        def main():
                news = fetch_latest_news()
                history = load_history()
                for article in news:
                            if article['link'] not in history:
                                            blog_post = generate_blog_post(article)
                                            if blog_post:
                                                                image_query = article['title'].split(':')[0]
                                                                image_url = search_unsplash_image(image_query)
                                                                if image_url:
                                                                                        blog_post['image'] = image_url
                                                                                    history.append(article['link'])
                                                                save_history(history)
                                                                time.sleep(5)

                                if __name__ == "__main__":
                                        main()
