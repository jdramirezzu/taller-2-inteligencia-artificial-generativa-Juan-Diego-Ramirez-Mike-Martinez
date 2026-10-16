# Fase 1: Selección de los componentes del sistema RAG

## Qué es lo que vamos a construir

En el Taller 1 el modelo solo podía responder dos tipos de preguntas: estado de un pedido y devolución de un pedido. Para eso le pasábamos los datos del pedido dentro del prompt.

Ahora el asistente debe responder **cualquier** pregunta de un cliente. Si la respuesta está en los documentos de EcoMarket, debe responderla. Si no está, debe decir que no tiene esa información.

Para eso usamos RAG (Generación Aumentada por Recuperación). Funciona así:

1. Los documentos de la empresa se cortan en pedazos pequeños (fragmentos).
2. Cada fragmento se convierte en una lista de números (un vector) con un **modelo de embeddings**. Dos textos con significado parecido quedan con vectores parecidos.
3. Los vectores se guardan en una **base de datos vectorial**.
4. Cuando llega una pregunta, también se convierte en vector y se buscan los fragmentos con los vectores más parecidos.
5. Esos fragmentos se ponen dentro del prompt y el **modelo generativo (LLM)** escribe la respuesta usando solo esa información.

Por eso hay que elegir tres componentes: el modelo de embeddings, la base de datos vectorial y el LLM.

---

## 1. Modelo de embeddings

### Qué necesita EcoMarket

- **Español:** todos los documentos y todas las preguntas de los clientes están en español. Un modelo entrenado solo en inglés compara mal los textos en español.
- **Costo bajo:** el proyecto está en fase de piloto (igual que en el Taller 1). No queremos pagar antes de saber si el sistema funciona.
- **Textos cortos:** los fragmentos tienen entre 200 y 650 caracteres (ver Fase 2). No necesitamos un modelo que lea documentos muy largos.
- **Pocos documentos:** en el piloto son 38 fragmentos. Aunque EcoMarket crezca a miles de productos, siguen siendo pocos para un modelo pequeño.

### Opciones que comparamos

| Modelo | Tipo | Español | Costo | Tamaño del vector | Comentario |
|---|---|---|---|---|---|
| `paraphrase-multilingual-MiniLM-L12-v2` (sentence-transformers) | Código abierto (Hugging Face) | Sí, entrenado en más de 50 idiomas | Gratis, corre en el computador | 384 | Pequeño (~470 MB), funciona en CPU. Es de los más usados para empezar. |
| `intfloat/multilingual-e5-base` | Código abierto (Hugging Face) | Sí | Gratis, corre en el computador | 768 | Mejor precisión en búsqueda que MiniLM según el ranking MTEB, pero más pesado y hay que agregar los prefijos "query:" y "passage:" a los textos. |
| `BAAI/bge-m3` | Código abierto (Hugging Face) | Sí | Gratis, pero pesado (~2.2 GB) | 1024 | Muy bueno con textos largos. Para fragmentos cortos como los nuestros es más de lo que necesitamos. |
| `text-embedding-3-small` (OpenAI) | Propietario (API) | Sí | Se paga por token (barato, pero no es gratis) | 1536 | Buena precisión. Necesita internet, otra API key y enviar los documentos de la empresa a un tercero. |

**Nota:** DeepSeek, el proveedor del LLM que usamos (ver sección 3), no ofrece un servicio de embeddings. Por eso de todas formas teníamos que escoger un modelo de embeddings aparte.

### Nuestra elección: `paraphrase-multilingual-MiniLM-L12-v2` (código abierto)

Razones:

1. **Maneja español.** Fue entrenado con pares de frases en muchos idiomas, incluido el español. En nuestras pruebas, para preguntas como "¿Cuánto tarda el reembolso si pagué con PSE?" el primer fragmento recuperado fue la sección "7. REEMBOLSOS" de la política, que es la correcta (ver `fase3_rag/resultados/`).
2. **Costo cero.** Corre en el computador, no se paga por usarlo. Indexar los 38 fragmentos tomó unos segundos en CPU.
3. **Los datos no salen de la empresa.** Los documentos se convierten en vectores localmente. Con un modelo propietario habría que enviarlos a la API de otra empresa.
4. **Fácil de usar.** LangChain lo carga con una sola clase (`HuggingFaceEmbeddings`) y no necesita prefijos especiales.

Desventaja que aceptamos: no es el modelo más preciso. Modelos como `multilingual-e5-base` o `bge-m3` tienen mejores resultados en los rankings de búsqueda. Como somos un piloto con pocos documentos, preferimos empezar con el más simple. Si en las pruebas el sistema trae fragmentos equivocados, el primer cambio sería probar `multilingual-e5-base`, porque solo hay que cambiar una línea en `config.py` y volver a indexar.

### Cómo afecta este componente al sistema

Si el modelo de embeddings es malo, la búsqueda trae fragmentos que no tienen que ver con la pregunta. En ese caso el LLM no tiene la información correcta y responde "no tengo información" o, peor, responde algo equivocado. Es decir: **el LLM solo puede ser tan bueno como los fragmentos que le llegan**.

---

## 2. Base de datos vectorial

### Qué necesita EcoMarket

- Guardar pocos vectores en el piloto (38) y, más adelante, algunos miles (catálogo completo, más preguntas frecuentes).
- Buscar rápido los vectores más parecidos a una pregunta.
- No tener costo mientras estamos probando.
- Ser fácil de instalar para un equipo pequeño.

### Opciones que comparamos

| | **ChromaDB** | **Pinecone** | **Weaviate** |
|---|---|---|---|
| Qué es | Base vectorial de código abierto que corre dentro del mismo programa de Python y guarda los datos en una carpeta | Servicio en la nube administrado (no se instala, se usa por API) | Base vectorial de código abierto. Se instala con Docker o se usa en su nube |
| Costo | Gratis | Tiene plan gratis con límites; después se paga por uso | Gratis si la instalas tú; la versión en la nube se paga |
| Facilidad de uso | Muy fácil: `pip install chromadb` y listo | Fácil, pero hay que crear una cuenta, un índice y manejar otra API key | Más difícil: hay que levantar un servidor y definir un esquema |
| Escalabilidad | Buena para miles o cientos de miles de vectores en un solo equipo. Para millones o muchos usuarios a la vez tiene menos herramientas | Muy alta: está hecha para millones de vectores y mucho tráfico | Alta: soporta varios servidores, filtros y búsqueda híbrida (palabras + vectores) |
| Datos | Quedan en el computador de la empresa | Quedan en servidores de Pinecone | Donde se instale |
| Integración con LangChain | Sí (`langchain-chroma`) | Sí | Sí |

### Nuestra elección: ChromaDB

Razones:

1. **Costo cero y sin cuentas extra.** Se instala con pip y guarda todo en la carpeta `chroma_db/`.
2. **Suficiente para el tamaño de EcoMarket.** Una tienda con cientos de productos y unas decenas de preguntas frecuentes genera pocos miles de fragmentos. Chroma busca en eso en milisegundos.
3. **Fácil para aprender.** El código queda corto y se puede ver cada paso (crear la colección, guardar, buscar).
4. **Guarda metadatos.** Cada fragmento lleva su fuente (`politica`, `catalogo`, `faq`). Así podemos mostrar de dónde salió cada respuesta.

Desventajas que aceptamos:

- Si EcoMarket creciera a millones de vectores o muchos agentes consultando al mismo tiempo, Chroma local se quedaría corto. En ese caso pasaríamos a Pinecone (si no queremos administrar servidores) o a Weaviate (si queremos mantener los datos en servidores propios).
- No hace búsqueda híbrida por palabras exactas tan completa como Weaviate. Para los números de pedido (ECM-XXXX) esto no es problema porque no los buscamos en la base vectorial (ver Fase 2).

### Cómo afecta este componente al sistema

La base vectorial no cambia **qué** fragmentos son parecidos (eso lo decide el modelo de embeddings). Lo que decide es **qué tan rápido y a qué escala** se puede hacer la búsqueda, cuánto cuesta y dónde quedan guardados los datos. Configuramos Chroma para medir la similitud con distancia coseno, que es la medida recomendada para este modelo de embeddings.

---

## 3. Modelo generativo (LLM): DeepSeek Flash

### Por qué cambiamos el modelo del Taller 1

En el Taller 1 probamos dos modelos locales y gratis:

- `qwen2.5:7b` (con Ollama): siguió bien las reglas del prompt.
- `Qwen2.5-1.5B-Instruct` (con Transformers): inventó datos. En un caso inventó que un producto "ya había sido instalado" y por eso negó una devolución que sí se podía hacer.

La conclusión del Taller 1 fue que el modelo más barato no siempre es el más barato, porque un error de negocio cuesta más que el modelo, y que si los modelos locales no alcanzaban había que probar uno más potente aunque fuera de pago.

En este taller el trabajo del modelo es más difícil que en el Taller 1:

- El prompt es más largo (datos del pedido + 4 fragmentos de documentos).
- Tiene que combinar información de dos fuentes (por ejemplo, el estado del pedido y la política de devoluciones).
- Tiene que reconocer cuándo la respuesta **no** está en el contexto y decirlo.

Por eso pasamos a un modelo más potente por API: **DeepSeek Flash** (`deepseek-flash`).

### Relación costo / calidad / beneficio

| Criterio | DeepSeek Flash | Modelos locales del Taller 1 |
|---|---|---|
| Costo | Se paga por uso: 0.15 a 0.30 USD por millón de tokens de entrada y 0.60 a 1.20 USD por millón de tokens de salida (precio de la página oficial de DeepSeek, octubre 2026). Una pregunta de nuestro sistema usa cerca de 1.000 tokens de entrada y 100 de salida, o sea menos de 0.001 USD por respuesta. | Gratis, pero necesitan un computador con buena memoria o GPU. |
| Calidad | Modelo grande, sigue instrucciones largas y maneja bien el español. | El de 7B funcionó; el de 1.5B inventó datos. |
| Contexto | Hasta 1 millón de tokens, sobra para nuestros prompts. | Menor. |
| Beneficio | Respuestas más confiables en los casos donde un error cuesta dinero (devoluciones, reembolsos). | Sirven para preguntas simples. |

Comparado con otros modelos de pago, DeepSeek Flash es de los más baratos. Por eso es una opción razonable para un piloto: probamos un modelo más potente sin gastar casi nada.

Decisiones para gastar el mínimo de saldo:

- **Apagamos el modo "thinking".** DeepSeek Flash razona antes de responder por defecto, y esos tokens también se cobran. Para respuestas cortas de soporte no hace falta.
- **Máximo 300 tokens de respuesta** y **temperatura 0** (respuestas más estables).
- **Solo 4 fragmentos** en el prompt (no todos los documentos).
- La búsqueda de fragmentos se puede probar sin llamar al modelo (`--solo-recuperar`), así que los ajustes de chunking no gastan saldo.

Riesgo que aceptamos: con una API externa, la pregunta del cliente y los fragmentos recuperados se envían a DeepSeek. Por eso no enviamos datos sensibles como números de tarjeta. En el contexto del pedido solo va el nombre del cliente, el producto y el estado.

---

## Resumen de la arquitectura

| Componente | Elección | Tipo |
|---|---|---|
| Framework | LangChain | Código abierto |
| Modelo de embeddings | `paraphrase-multilingual-MiniLM-L12-v2` | Código abierto, local |
| Base de datos vectorial | ChromaDB | Código abierto, local |
| LLM | DeepSeek Flash (`deepseek-flash`) | Propietario, por API |
| Consulta de pedidos | Búsqueda exacta en `pedidos.json` (del Taller 1) | Código propio |

```
Pregunta del cliente
      │
      ├──► ¿Trae número ECM-XXXX? ──► sí ──► buscar el pedido en pedidos.json
      │
      ├──► Modelo de embeddings ──► vector de la pregunta
      │                                   │
      │                                   ▼
      │                       ChromaDB: 4 fragmentos más parecidos
      │                                   │
      ▼                                   ▼
   Prompt = reglas + datos del pedido + fragmentos + pregunta
      │
      ▼
   DeepSeek Flash ──► respuesta (o "No tengo información sobre eso...")
```
