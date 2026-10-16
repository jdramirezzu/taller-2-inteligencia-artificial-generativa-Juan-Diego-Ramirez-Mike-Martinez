# Fase 2: Creación de la base de conocimiento

Un sistema RAG solo puede responder bien si encuentra el fragmento correcto. Si el documento tiene información mala o si se corta mal, la búsqueda trae fragmentos incompletos y el modelo responde mal. Por eso en esta fase definimos **qué documentos** usamos y **cómo los cortamos**.

Los archivos están en `fase3_rag/data/`.

---

## 1. Identificación de documentos

Escogimos 3 tipos de documentos, cada uno en un formato distinto, porque así llegan normalmente en una empresa de e-commerce. Además mantenemos el archivo de pedidos del Taller 1.

| # | Documento | Formato | Qué contiene | Qué preguntas responde |
|---|---|---|---|---|
| 1 | `politica_devoluciones_y_envios.pdf` | PDF | 12 secciones numeradas: plazo de devolución, productos que no se devuelven, condiciones, pasos, productos dañados, reembolsos, cambios, envíos, retrasos, cancelaciones y contacto | "¿Cuánto tengo para devolver?", "¿Cuánto tarda el reembolso?", "¿Hacen envíos internacionales?" |
| 2 | `catalogo_productos.csv` | Hoja de cálculo (CSV) | 14 productos con SKU, nombre, categoría, precio, stock, si se puede devolver, descripción, materiales y cuidados | "¿Cuánto cuesta el panel solar?", "¿Hay botellas disponibles?", "¿De qué está hecha la mochila?" |
| 3 | `preguntas_frecuentes.json` | JSON | 12 preguntas con su respuesta, agrupadas por tema (pagos, pedidos, productos, empaque, cuenta, facturación, programa de puntos, tiendas) | "¿Puedo pagar en cuotas?", "¿Tienen tiendas físicas?", "¿Cómo pido factura?" |
| — | `pedidos.json` (del Taller 1) | JSON | 11 pedidos de prueba con estado, fechas y si el producto es devolvible | "¿Dónde está mi pedido ECM-1004?" |

**Por qué estos documentos:** en el Taller 1 vimos que la mayoría de consultas son sobre estado de pedidos, devoluciones y características de productos. La política cubre las devoluciones y los envíos, el catálogo cubre los productos y las preguntas frecuentes cubren el resto de dudas repetitivas.

**Por qué los pedidos NO van a la base vectorial:** una búsqueda por similitud trae "lo más parecido", no "lo exacto". Los números `ECM-1004` y `ECM-1005` se parecen mucho como texto, y la búsqueda podría traer el pedido equivocado. Por eso los pedidos se siguen buscando como en el Taller 1: por su número exacto. El sistema detecta el número dentro del mensaje con una expresión regular (`ECM-\d{4}`).

**Calidad de los documentos:** antes de indexar revisamos que:

- Los datos no se contradigan entre documentos. Por ejemplo, el catálogo dice que el yogur "no" se puede devolver, y la política dice lo mismo para alimentos perecederos.
- Los productos del catálogo sean los mismos de `pedidos.json`, para que el modelo pueda combinar un pedido con la información del producto.
- Cada sección de la política hable de un solo tema. Así un fragmento responde una sola cosa.

---

## 2. Segmentación (chunking)

### Las estrategias que existen

| Estrategia | Cómo funciona | Ventaja | Desventaja |
|---|---|---|---|
| **Tamaño fijo** | Corta el texto cada N caracteres (por ejemplo, 500), sin importar dónde quede el corte. Normalmente se deja un solapamiento (overlap) para no perder lo que queda en el borde. | Muy simple. Todos los fragmentos tienen el mismo tamaño. | Puede cortar una frase o una lista por la mitad. Un fragmento puede quedar con el final de un tema y el inicio de otro. |
| **Por párrafos** | Corta donde hay un salto de línea doble (fin de párrafo). | Respeta las ideas completas. | Los párrafos pueden ser muy largos o muy cortos. Depende de que el documento tenga los párrafos bien marcados. |
| **Recursiva** | Intenta cortar primero por el separador más grande (párrafo). Si el pedazo sigue muy grande, prueba con el siguiente (línea, luego frase, luego palabra), hasta que quede del tamaño pedido. Es `RecursiveCharacterTextSplitter` en LangChain. | Respeta la estructura cuando puede y garantiza un tamaño máximo. | Necesita escoger bien el tamaño y los separadores. |
| **Por estructura del documento** | Corta usando la estructura propia del archivo: una fila de una tabla, un registro de un JSON, una sección con título. | Cada fragmento es una unidad con sentido completo. | Hay que escribir una regla distinta para cada tipo de documento. |

### Lo que decidimos para cada documento

No usamos una sola estrategia para todo, porque los tres documentos tienen formas distintas.

**1. Preguntas frecuentes (JSON): 1 fragmento por pregunta.**
Cada fragmento es `Pregunta: ... Respuesta: ...`. Una pregunta y su respuesta forman una unidad completa. Si cortáramos por tamaño fijo, la pregunta podría quedar en un fragmento y la respuesta en otro, y la búsqueda encontraría la pregunta sin la respuesta. Además dejamos la pregunta dentro del fragmento porque se parece mucho a como escribe el cliente, y eso ayuda a la búsqueda.

**2. Catálogo (CSV): 1 fragmento por producto (fila).**
Cada fila se convierte en un texto con etiquetas, por ejemplo:

```
Producto: Panel solar portátil 20W (SKU ECO-005).
Categoría: electronica.
Precio: 289.000 COP.
Stock: 14 unidades disponibles.
¿Se puede devolver?: sí.
...
```

Si cortáramos el CSV por tamaño fijo, el precio de un producto podría quedar pegado al nombre de otro producto, y el modelo daría el precio equivocado. Escribir la fila como frases con etiquetas ayuda al modelo de embeddings, que fue entrenado con texto y no con tablas. También cambiamos el stock 0 por la palabra "AGOTADO", que es más fácil de entender para el modelo.

**3. Política (PDF): 1 fragmento por sección numerada + splitter recursivo de respaldo.**
Primero intentamos cortar por párrafos, pero al leer el PDF con `PyPDFLoader` vimos que **el PDF pierde las líneas en blanco** entre párrafos y además corta las frases largas con saltos de línea. Por eso el corte por párrafos no funcionaba.

Lo que hicimos:

1. Unir las líneas que el PDF había partido (se reemplaza `" \n"` por `" "`).
2. Cortar el texto donde empieza un título de sección (por ejemplo `7. REEMBOLSOS`), usando una expresión regular.
3. Si una sección tiene más de 700 caracteres, se corta con `RecursiveCharacterTextSplitter` (separadores: salto de línea, punto, espacio) con 100 caracteres de solapamiento, y cada pedazo lleva el título de la sección para no perder el tema.

En nuestro PDF ninguna sección pasa de 700 caracteres (la más larga tiene 621), así que quedaron 12 fragmentos, uno por sección. El splitter recursivo queda listo por si la política crece.

**Por qué es mejor que tamaño fijo para este caso:** probamos cortar la política cada 500 caracteres. Un fragmento terminó así:

```
...- Productos de higiene personal que ya fueron abiertos o usados (por ejemp
```

y el siguiente empezó así:

```
lo: cepillos de dientes, desodorantes, jabones, cremas).
- Productos de higiene personal sin abrir sí se pueden devolver dentro de los 30 días...
```

Si un cliente pregunta "¿puedo devolver un desodorante?", la búsqueda probablemente trae el segundo fragmento, porque es el que dice "desodorantes". Ese fragmento solo tiene la regla "sin abrir sí se pueden devolver" y no tiene la regla "abiertos no se devuelven". El modelo podría decir que sí se puede devolver un desodorante ya usado. Cortar por sección mantiene la regla y su excepción en el mismo fragmento.

### Resultado

| Documento | Estrategia | Fragmentos | Tamaño (caracteres) |
|---|---|---|---|
| Política (PDF) | Por sección + recursivo de respaldo | 12 | 190 a 621 |
| Catálogo (CSV) | Por fila | 14 | 292 a 375 |
| Preguntas frecuentes (JSON) | Por registro | 12 | 184 a 292 |
| **Total** | | **38** | |

Los fragmentos se pueden ver con `python src/cargar_documentos.py`.

### Cómo afecta el chunking al RAG

- **Fragmentos muy grandes:** mezclan temas. El vector queda como un promedio de varios temas y la búsqueda es menos precisa. Además el prompt queda más largo y cuesta más.
- **Fragmentos muy pequeños:** pierden contexto. Por ejemplo, "entre 3 y 5 días hábiles" sin decir que es para PSE.
- **Fragmentos que cortan una idea:** el modelo recibe media regla y puede responder algo incorrecto.

Con nuestros tamaños (entre 184 y 621 caracteres) cada fragmento responde una pregunta concreta.

---

## 3. Indexación

La indexación es el proceso que toma los fragmentos y los deja guardados en la base de datos vectorial para poder buscarlos. Se hace una vez, antes de usar el asistente, con `python src/indexar.py`. Los pasos son:

1. **Cargar y cortar.** `cargar_documentos.py` lee los tres archivos y devuelve una lista de 38 objetos `Document` de LangChain. Cada uno tiene:
   - `page_content`: el texto del fragmento.
   - `metadata`: de dónde salió (`fuente`, `tipo` y un `id`, por ejemplo `ECO-005` o `7. REEMBOLSOS`).
2. **Cargar el modelo de embeddings.** `HuggingFaceEmbeddings` descarga `paraphrase-multilingual-MiniLM-L12-v2` la primera vez y después lo usa desde el disco. Usamos `normalize_embeddings=True` para que todos los vectores tengan largo 1.
3. **Convertir cada fragmento en vector.** El modelo convierte cada texto en un vector de **384 números**.
4. **Guardar en ChromaDB.** `Chroma.from_documents(...)` guarda, para cada fragmento, el vector, el texto y los metadatos en la colección `ecomarket_conocimiento`, dentro de la carpeta `chroma_db/`. Configuramos la colección con distancia coseno (`hnsw:space = cosine`). Chroma arma un índice HNSW, que permite encontrar los vectores más cercanos sin comparar la pregunta contra todos uno por uno.
5. **Borrar antes de volver a indexar.** Si se ejecuta `indexar.py` dos veces, primero se borra la carpeta `chroma_db/`. Así no quedan fragmentos repetidos.

Cuando llega una pregunta se hace lo mismo con la pregunta: se convierte en un vector de 384 números con **el mismo modelo** y Chroma devuelve los 4 fragmentos con menor distancia coseno. Es importante usar el mismo modelo para indexar y para buscar, porque los vectores de modelos distintos no se pueden comparar.

Si EcoMarket cambia un documento (por ejemplo, actualiza precios en el CSV), hay que volver a ejecutar `indexar.py`.
