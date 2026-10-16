# Fase 3: Integración y ejecución del código RAG

Código del asistente de EcoMarket con RAG. Usa **LangChain** para unir las piezas, **ChromaDB** como base vectorial, `paraphrase-multilingual-MiniLM-L12-v2` como modelo de embeddings y **DeepSeek Flash** como LLM. La elección de cada componente está explicada en [`../fase1_componentes/seleccion_componentes.md`](../fase1_componentes/seleccion_componentes.md) y la preparación de los documentos en [`../fase2_base_conocimiento/base_conocimiento.md`](../fase2_base_conocimiento/base_conocimiento.md).

## Estructura

```
fase3_rag/
├── data/
│   ├── politica_devoluciones_y_envios.pdf   # documento 1 (PDF)
│   ├── catalogo_productos.csv               # documento 2 (hoja de cálculo)
│   ├── preguntas_frecuentes.json            # documento 3 (JSON)
│   ├── pedidos.json                         # pedidos del Taller 1 (búsqueda exacta, no vectorial)
│   └── fuentes/politica_...txt              # texto con el que se generó el PDF
├── src/
│   ├── config.py             # todos los parámetros (modelos, k, chunk size, rutas)
│   ├── cargar_documentos.py  # carga los 3 documentos y los corta en fragmentos
│   ├── indexar.py            # fragmentos -> embeddings -> ChromaDB
│   ├── pedidos_tool.py       # búsqueda de pedidos por número (del Taller 1)
│   ├── prompts.py            # los 3 prompts que comparamos
│   ├── rag_chat.py           # el asistente: recuperación + prompt + DeepSeek
│   └── evaluar.py            # corre los experimentos y guarda los resultados
├── resultados/resultados_experimentos.md    # respuestas reales del modelo
├── comparacion_resultados.md                # análisis de los experimentos
├── limitaciones_y_suposiciones.md
├── requirements.txt
└── .env.example
```

## Instalación

Se probó con Python 3.12 (ChromaDB todavía puede fallar con Python 3.14).

```bash
cd fase3_rag
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env      # y escribir la API key de DeepSeek dentro de .env
```

La primera vez se descarga el modelo de embeddings desde Hugging Face (~470 MB).

## Cómo ejecutar

```bash
cd src

# 1. Ver los fragmentos (no gasta saldo)
python cargar_documentos.py

# 2. Crear la base vectorial (una vez, o cuando cambien los documentos)
python indexar.py

# 3. Ver qué fragmentos trae la búsqueda para una pregunta (no gasta saldo)
python rag_chat.py --pregunta "¿Cuánto tarda el reembolso si pagué con PSE?" --solo-recuperar

# 4. Hacer una pregunta al asistente
python rag_chat.py --pregunta "Quiero devolver mi pedido ECM-1005, ¿cómo hago?"

# 5. Comparar la misma pregunta sin RAG y con RAG
python rag_chat.py --pregunta "¿Hacen envíos a México?" --modo ambos

# 6. Otras opciones: otro prompt o menos fragmentos
python rag_chat.py --pregunta "¿Venden paneles solares de 100W?" --modo rag_sin_reglas
python rag_chat.py --pregunta "Mi pedido ECM-1004 está retrasado, ¿lo puedo cancelar?" --k 1

# 7. Chat en la terminal
python rag_chat.py --interactivo

# 8. Correr todos los experimentos (25 llamadas) y guardar resultados/resultados_experimentos.md
python evaluar.py
```

---

## Explicación del código, sección por sección

### `config.py`
Junta todos los valores que se pueden cambiar: rutas de los archivos, nombre del modelo de embeddings, tamaño de los fragmentos, cuántos fragmentos se recuperan (`K_FRAGMENTOS = 4`) y la configuración de DeepSeek. Lee la API key del archivo `.env` con `python-dotenv`, para que la key no quede escrita en el código.

### `cargar_documentos.py` — carga y chunking
Tiene una función por tipo de documento. Todas devuelven una lista de `Document` de LangChain (texto + metadatos).

- `cargar_faq()`: lee el JSON y crea un `Document` por cada pregunta, con el texto `Pregunta: ... Respuesta: ...`.
- `cargar_catalogo()`: lee el CSV con `csv.DictReader` y convierte cada fila en un texto con etiquetas (`Producto:`, `Precio:`, `Stock:`...). Si el stock es 0 escribe "AGOTADO".
- `cargar_politica()`: lee el PDF con `PyPDFLoader`, une las líneas partidas, separa por títulos de sección con una expresión regular y, si una sección es muy larga, la corta con `RecursiveCharacterTextSplitter`.
- `cargar_todos()`: junta las tres listas (38 fragmentos).

### `indexar.py` — embeddings y base vectorial
- `obtener_embeddings()`: crea el modelo de embeddings `HuggingFaceEmbeddings` con los vectores normalizados.
- `main()`: borra la base anterior, carga los fragmentos y llama a `Chroma.from_documents(...)`. Esa función convierte cada fragmento en un vector de 384 números y lo guarda en `chroma_db/` junto con el texto y los metadatos.
- `abrir_base_vectorial()`: la usa `rag_chat.py` para abrir la base ya creada. Usa el **mismo** modelo de embeddings, porque la pregunta se tiene que convertir en vector igual que los fragmentos.

### `pedidos_tool.py` — lo que viene del Taller 1
Busca un pedido por su número exacto en `pedidos.json` y lo convierte en texto para el prompt. Lo nuevo es `detectar_tracking()`, que encuentra un número `ECM-XXXX` dentro del mensaje del cliente. Así ya no hace falta pasar el número aparte como en el Taller 1.

### `prompts.py` — los prompts
En el Taller 1 había dos prompts (pedido y devolución). Ahora hay un solo prompt para cualquier pregunta, con dos espacios para contexto: `{contexto_pedido}` y `{contexto_documentos}`. Hay tres versiones para comparar:

| Prompt | Documentos | Reglas para no inventar |
|---|---|---|
| `PROMPT_SIN_RAG` | No | No (solo tono y largo) |
| `PROMPT_RAG` | Sí | Sí. Si la respuesta no está en el contexto, responde un mensaje fijo: "No tengo información sobre eso..." |
| `PROMPT_RAG_SIN_REGLAS` | Sí | No |

Los prompts usan `ChatPromptTemplate` con un mensaje de sistema (instrucciones + contexto) y un mensaje humano (la pregunta).

### `rag_chat.py` — el asistente (aquí se conectan las piezas)
- `crear_llm()`: crea el modelo con `ChatOpenAI`. DeepSeek usa el mismo formato de API que OpenAI, así que solo se cambia la `base_url` y el nombre del modelo. Aquí se apaga el modo "thinking" y se limita la respuesta a 300 tokens para gastar menos saldo.
- `recuperar()`: llama a `similarity_search_with_score` de Chroma. Convierte la pregunta en vector y devuelve los k fragmentos más cercanos con su distancia coseno (más cerca de 0 = más parecido).
- `formatear_fragmentos()`: pone los fragmentos como texto numerado con su fuente para meterlos en el prompt.
- `AsistenteEcoMarket.responder()`: es el flujo completo:
  1. Detecta el número de pedido y busca el pedido (Taller 1).
  2. Recupera los fragmentos de Chroma (si el modo no es `sin_rag`).
  3. Arma la cadena `prompt | llm` de LangChain (el operador `|` pasa la salida del prompt como entrada al modelo) y la ejecuta con `invoke`.
  4. Devuelve la respuesta, los fragmentos usados y los tokens consumidos (para calcular el costo).

### `evaluar.py` — los experimentos
Corre 10 preguntas de prueba en los modos `sin_rag` y `rag`, más los experimentos de cambio de prompt y cambio de k. Guarda todo en `resultados/resultados_experimentos.md` con los fragmentos, las respuestas y el consumo de tokens.

---

## Qué cambió respecto al Taller 1

| | Taller 1 | Taller 2 |
|---|---|---|
| Preguntas que responde | Solo estado de pedido y devolución | Cualquier pregunta; si no sabe, lo dice |
| Contexto | Datos de un pedido | Datos del pedido + fragmentos de 3 documentos |
| Prompts | 2 (uno por ejercicio) | 1 para todo |
| Número de pedido | Se pasaba con `--tracking` | Se detecta dentro del mensaje (o `--tracking`) |
| Modelo | `qwen2.5:7b` (Ollama) y `Qwen2.5-1.5B` (Transformers), locales | DeepSeek Flash por API |
| Framework | Código propio | LangChain |

Los resultados y el análisis están en [`comparacion_resultados.md`](comparacion_resultados.md). Las limitaciones están en [`limitaciones_y_suposiciones.md`](limitaciones_y_suposiciones.md).
