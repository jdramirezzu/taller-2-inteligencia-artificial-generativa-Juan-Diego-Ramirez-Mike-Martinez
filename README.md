# Taller Práctico #2 — Sistema RAG para la atención al cliente de EcoMarket

Repositorio de entrega del Taller 2 (Maestría en Inteligencia Artificial Generativa). Continúa el Taller 1 (asistente con prompts para estado de pedido y devolución): ahora el asistente consulta los documentos de EcoMarket antes de responder (RAG), para poder contestar cualquier pregunta o decir que no tiene la información.

## Contenido

| Fase | Archivo | Qué contiene |
|---|---|---|
| Fase 1 — Selección de componentes | [`fase1_componentes/seleccion_componentes.md`](fase1_componentes/seleccion_componentes.md) | Modelo de embeddings, base de datos vectorial y LLM elegidos, con sus ventajas y desventajas |
| Fase 2 — Base de conocimiento | [`fase2_base_conocimiento/base_conocimiento.md`](fase2_base_conocimiento/base_conocimiento.md) | Los 3 documentos, la estrategia de chunking y el proceso de indexación |
| Fase 3 — Código | [`fase3_rag/`](fase3_rag/) | Código ejecutable con LangChain + ChromaDB + DeepSeek Flash |
| Fase 3 — Explicación del código | [`fase3_rag/README.md`](fase3_rag/README.md) | Instalación, ejecución y explicación de cada archivo |
| Fase 3 — Resultados | [`fase3_rag/comparacion_resultados.md`](fase3_rag/comparacion_resultados.md) | Sin RAG vs con RAG, cambio de prompt y cambio de k |
| Fase 3 — Limitaciones | [`fase3_rag/limitaciones_y_suposiciones.md`](fase3_rag/limitaciones_y_suposiciones.md) | Límites de recursos y suposiciones |

## Componentes elegidos

| Componente | Elección |
|---|---|
| Framework | LangChain |
| Embeddings | `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` (código abierto, local) |
| Base vectorial | ChromaDB (local) |
| LLM | DeepSeek Flash (`deepseek-flash`, por API) |

## Ejecución rápida

```bash
cd fase3_rag
python3.12 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # escribir la API key de DeepSeek
cd src
python indexar.py
python rag_chat.py --pregunta "¿Cuánto tarda el reembolso si pagué con PSE?"
```
