import os
import subprocess

folders = ["memory", "specs", "tests", "doc", ".streamlit"]

files = {
    "memory/activeContext.md": "# Contexto Activo\n",
    "memory/progress.md": "# Progreso\n",
    "doc/constitution.md": "# Constitución Global\n\n1. Código modular.\n2. Pruebas TDD estrictas.\n3. Cero secretos expuestos.",
    "AGENTS.md": "# Directorio de Agentes\n",
    ".streamlit/secrets.example.toml": "# api_key = 'TU_KEY'",
    ".gitignore": ".streamlit/secrets.toml\n.env\n__pycache__/\n.pytest_cache/\nvenv/\n",
    "app.py": "import streamlit as st\n\nst.set_page_config(page_title='App Deportiva')\nst.title('App en Construcción')",
    "requirements.txt": "streamlit\npandas\nplotly\npytest\nscipy\nstatsmodels\nscikit-learn\nnumpy",
    "tests/__init__.py": "",
    "tests/test_basic.py": "def test_ambiente_configurado():\n    assert True"
}

def setup():
    print("🚀 Creando estructura base...")
    for folder in folders:
        os.makedirs(folder, exist_ok=True)
    for filepath, content in files.items():
        if not os.path.exists(filepath):
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(content)
    
    # Git automático
    try:
        subprocess.run(["git", "init"], check=True)
        subprocess.run(["git", "add", "."], check=True)
        subprocess.run(["git", "commit", "-m", "chore: inicializa estructura"], check=True)
        print("✅ Git configurado.")
    except Exception:
        pass

    # Instalar requerimientos automáticamente
    print("📦 Instalando librerías automáticamente...")
    subprocess.run(["pip", "install", "-r", "requirements.txt"])
    print("🎉 TODO LISTO. Ve a Copilot Chat.")

if __name__ == "__main__":
    setup()