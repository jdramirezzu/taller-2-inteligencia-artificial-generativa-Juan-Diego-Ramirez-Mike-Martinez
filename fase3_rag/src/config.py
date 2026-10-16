"""Configuración del sistema RAG de EcoMarket.

Todos los valores que se pueden cambiar para experimentar están aquí,
para no tener que buscarlos dentro del código.
"""
import os
from pathlib import Path

from dotenv import load_dotenv

# Carpetas del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CHROMA_DIR = BASE_DIR / "chroma_db"  # aquí Chroma guarda los vectores en disco
RESULTADOS_DIR = BASE_DIR / "resultados"

# Documentos de la base de conocimiento
RUTA_POLITICA_PDF = DATA_DIR / "politica_devoluciones_y_envios.pdf"
RUTA_CATALOGO_CSV = DATA_DIR / "catalogo_productos.csv"
RUTA_FAQ_JSON = DATA_DIR / "preguntas_frecuentes.json"
RUTA_PEDIDOS_JSON = DATA_DIR / "pedidos.json"  # no se indexa, se consulta por número exacto

# Modelo de embeddings (open source, Hugging Face, corre local y gratis)
MODELO_EMBEDDINGS = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"

# Base de datos vectorial
NOMBRE_COLECCION = "ecomarket_conocimiento"

# Chunking de la política (el PDF es el único documento que se corta con splitter)
CHUNK_SIZE = 700
CHUNK_OVERLAP = 100

# Recuperación: cuántos fragmentos se le pasan al modelo
K_FRAGMENTOS = 4

# Modelo generativo: DeepSeek Flash por API (compatible con el formato de OpenAI)
load_dotenv(BASE_DIR / ".env")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
DEEPSEEK_BASE_URL = "https://api.deepseek.com"
MODELO_LLM = "deepseek-flash"
MAX_TOKENS_RESPUESTA = 300  # límite de salida para gastar poco saldo
TEMPERATURA = 0.0  # respuestas más estables entre ejecuciones
