from google import genai
import os

def generate_blog_post(original_title, original_content):
    """Uses Gemini API to write a blog post based on the news."""
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("GEMINI_API_KEY no encontrada. Ejecutando en modo MOCK (Simulación).")
        return None
    
    try:
        client = genai.Client(api_key=api_key)
        
        prompt = f"""
        Eres un periodista experto en Inteligencia Artificial y tecnología en Argentina.
        Reescribe y expande la siguiente noticia para un blog especializado.
        Usa un tono informativo, profesional pero fácil de entender.
        Usa formato Markdown.
        
        Título original: {original_title}
        
        Contenido original o extracto:
        {original_content[:3000]}
        
        Devuelve EXACTAMENTE el siguiente formato y NADA MÁS:
        
        [TITULO]
        (Aquí el nuevo título atractivo)
        [DESCRIPCION]
        (Una breve descripción de 1 línea para SEO)
        [CONTENIDO]
        (Aquí el cuerpo completo del artículo en Markdown. Usa párrafos, negritas y subtítulos si es necesario).
        """
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt,
        )
        text = response.text
        
        # Parse the custom format
        title = text.split('[TITULO]')[1].split('[DESCRIPCION]')[0].strip()
        description = text.split('[DESCRIPCION]')[1].split('[CONTENIDO]')[0].strip()
        content = text.split('[CONTENIDO]')[1].strip()
        
        return {
            "title": title,
            "description": description,
            "content": content
        }
        
    except Exception as e:
        print(f"Error con la API de Gemini: {e}")
        return None
