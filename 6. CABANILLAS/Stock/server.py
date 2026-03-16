import re
from flask import Flask, render_template_string, send_from_directory
import markdown
import os

app = Flask(__name__)
VAULT_DIR = r"C:\ruta\a\tu\boveda"

def process_obsidian_links(content):
    """
    Convierte [[Etiqueta]] en enlaces HTML estándar.
    """
    def replace_link(match):
        label = match.group(1)
        # Convierte a un enlace a la vista del archivo
        return f'<a href="/view/{label}.md">{label}</a>'
    
    # Busca patrones [[Etiqueta]] y reemplázalos
    return re.sub(r'\[\[([^\]]+)\]\]', replace_link, content)

@app.route("/")
def index():
    files = [f for f in os.listdir(VAULT_DIR) if f.endswith(".md")]
    return render_template_string("""
    <h1>Archivos de la Bóveda</h1>
    <ul>
        {% for file in files %}
            <li><a href="/view/{{ file }}">{{ file }}</a></li>
        {% endfor %}
    </ul>
    """, files=files)

@app.route("/view/<filename>")
def view_file(filename):
    path = os.path.join(VAULT_DIR, filename)
    if not os.path.exists(path):
        return f"Archivo {filename} no encontrado.", 404

    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Procesa los enlaces de Obsidian
    content = process_obsidian_links(content)
    # Convierte Markdown a HTML
    html_content = markdown.markdown(content)
    return render_template_string("""
    <h1>{{ filename }}</h1>
    <div>{{ content|safe }}</div>
    <a href="/">Volver a la lista</a>
    """, filename=filename, content=html_content)

@app.route("/static/<path:path>")
def static_files(path):
    return send_from_directory(VAULT_DIR, path)

if __name__ == "__main__":
    app.run(debug=True, port=8000)
