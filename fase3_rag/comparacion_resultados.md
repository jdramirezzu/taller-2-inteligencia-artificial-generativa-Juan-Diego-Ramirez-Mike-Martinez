# Comparación de resultados

Las respuestas completas, con los fragmentos recuperados y los tokens de cada llamada, están en [`resultados/resultados_experimentos.md`](resultados/resultados_experimentos.md). Se generaron con `python src/evaluar.py` el 2026-10-16.

- Modelo: `deepseek-flash` (thinking apagado, temperatura 0, máximo 300 tokens).
- Embeddings: `paraphrase-multilingual-MiniLM-L12-v2`. Base vectorial: ChromaDB.
- **Costo total de los 25 experimentos: 0.0069 USD** (13.227 tokens de entrada y 2.411 de salida).

Hicimos tres cambios para ver cómo cambia el comportamiento del modelo:

1. Quitar y poner el RAG (mismo modelo, misma pregunta).
2. Quitar las reglas del prompt (dejando el RAG).
3. Bajar la cantidad de fragmentos recuperados de 4 a 1.

---

## Experimento 1: sin RAG vs con RAG

En el modo **sin RAG** el modelo solo recibe los datos del pedido (como en el Taller 1). En el modo **con RAG** recibe además los 4 fragmentos más parecidos a la pregunta.

| # | Pregunta | Sin RAG | Con RAG | ¿Correcto con RAG? |
|---|---|---|---|---|
| P1 | ¿Cuánto tarda el reembolso con PSE? | **Inventa:** "5 a 10 días hábiles". | "Entre 3 y 5 días hábiles", como dice la política. | Sí |
| P2 | ¿Cuánto cuesta el panel solar y cuántos hay? | **Inventa:** "desde $1.200.000 COP". | "289.000 COP y hay 14 unidades". | Sí |
| P3 | ¿Tienen programa de puntos? | Acierta el nombre "EcoPuntos" y la regla de 1 punto por 1.000 COP (coincidencia), pero **inventa** "descuentos por temporada y para clientes frecuentes". | Da las reglas exactas: 100 puntos = 10.000 COP, vencen a los 12 meses. | Sí |
| P4 | Devolver el pedido ECM-1005 | Sabe que está dentro de los 30 días (eso viene del pedido), pero **inventa el proceso**: "escríbenos al correo de servicio al cliente". | Da los pasos reales: "Mis pedidos" → "Solicitar devolución" → guía prepagada en 2 días hábiles, envío gratis. | Sí |
| P5 | ECM-1003, snacks vencidos | **Inventa un correo**: servicioalcliente@ecomarket.com.co. | Dice correctamente que, aunque los perecederos no se devuelven, si llegó vencido tiene derecho a una solución. No dice cuál es la solución (ver hallazgo abajo). | Parcial |
| P6 | ECM-1004 retrasado, ¿lo puedo cancelar? | **Error de negocio:** dice que "sí es posible cancelarlo" porque no ha sido entregado. Según la política, un pedido despachado solo se cancela si el retraso supera 5 días hábiles. | Aplica la regla de los 5 días hábiles después de la fecha estimada (2026-09-13) y explica el motivo del retraso sin decir "notas internas". | Sí |
| P7 | ¿Hacen envíos a México? | Responde bien ("solo dentro de Colombia"), por suerte. | "No hace envíos internacionales por ahora", como dice la política. | Sí |
| P8 | ¿Venden paneles de 100W? | **Inventa:** "sí contamos con paneles solares de 100W". | "No tengo información sobre eso..." | Sí |
| P9 | ¿Cuál es la capital de Francia? | Responde "París" (no es tema de EcoMarket). | "No tengo información sobre eso..." | Sí |
| P10 | ¿Dónde está mi pedido? (sin número) | Pide el número o el correo. | Pide el número en formato ECM-XXXX y menciona "Mis pedidos" (sale de las preguntas frecuentes). | Sí |

### Qué aprendimos

- **Sin RAG el modelo inventa con seguridad.** En 7 de 10 preguntas (P1 a P6 y P8) dio datos falsos sin avisar que no los sabía: precios, plazos, un correo, descuentos y un producto que no existe. El caso más grave es P6, porque le dice al cliente que puede cancelar un pedido cuando la política no lo permite todavía. Es el mismo tipo de error que vimos en el Taller 1 con el modelo pequeño, pero ahora con un modelo grande: **el tamaño del modelo no reemplaza los datos de la empresa.**
- **Con RAG las respuestas salen de los documentos.** 9 de 10 respuestas fueron correctas y 1 fue parcial.
- **El asistente ya puede decir "no sé".** En P8 y P9 respondió el mensaje fijo. Esto era el objetivo del taller: responder cualquier pregunta o decir que no tiene la información.
- **Combina las dos fuentes.** En P4, P5 y P6 usó los datos del pedido (fecha de entrega, si es devolvible, motivo del retraso) junto con la política.
- **Costo:** con RAG cada llamada usa unos 900 tokens de entrada en vez de 110, porque el prompt lleva los 4 fragmentos. Aun así cada respuesta cuesta menos de 0.0005 USD.

### Hallazgo: la búsqueda no encontró la sección 6 en P5

En P5 el modelo dijo que el cliente "tiene derecho a una solución según la sección 6", pero no dijo cuál solución (cambio o reembolso, reportar en máximo 5 días con foto). Revisamos los fragmentos y **la sección "6. PRODUCTOS DAÑADOS, VENCIDOS O EQUIVOCADOS" no fue recuperada**. El modelo solo leyó la frase "(ver sección 6)" dentro de la sección 3.

Con `--solo-recuperar --k 10` vimos que la sección 6 ni siquiera está entre los 10 fragmentos más parecidos a "Me llegó el pedido ECM-1003 y los snacks estaban vencidos. ¿Qué puedo hacer?", aunque su título contiene la palabra "VENCIDOS". El modelo de embeddings pequeño le dio más peso a "pedido" y "snacks" que a "vencidos".

Lo bueno es que el modelo **no inventó** la solución: dijo lo que sabía y mandó al cliente al chat. Para corregirlo se podría:

1. Probar un modelo de embeddings más preciso (por ejemplo `multilingual-e5-base`, como dijimos en la Fase 1).
2. Agregar una pregunta frecuente "¿Qué hago si un producto llega dañado o vencido?", que se parece más a como escribe el cliente.

Esto muestra lo que explicamos en la Fase 1: **si la búsqueda no trae el fragmento, el LLM no puede usarlo**, aunque el modelo sea bueno.

---

## Experimento 2: quitar las reglas del prompt

Usamos `PROMPT_RAG_SIN_REGLAS`: recibe los mismos fragmentos, pero solo dice "Responde la pregunta del cliente. Puedes usar esta información".

| # | Con reglas (`PROMPT_RAG`) | Sin reglas (`PROMPT_RAG_SIN_REGLAS`) |
|---|---|---|
| P5 | 1 párrafo, 105 tokens. | Respuesta larga con negritas y lista numerada (375 tokens, llegó al límite). Promete "reemplazo o reembolso", que no estaba en los fragmentos recuperados (la sección 6 no llegó). Es correcto según la política, pero el modelo lo supuso. |
| P8 | "No tengo información sobre eso..." | Dice que no hay paneles de 100W y ofrece el de 20W con todos sus datos. Más útil para el cliente, pero largo y con emojis. |
| P9 | "No tengo información sobre eso..." | Responde "París". |

### Qué aprendimos

- **Las reglas controlan el formato y el largo.** Sin ellas el modelo escribe 3 o 4 veces más, con markdown y emojis. Eso cuesta más tokens y no se ve bien en un chat de soporte.
- **Las reglas evitan que el modelo complete con lo que supone.** En P5 sin reglas prometió una solución que no estaba en el contexto recuperado. Esta vez acertó, pero en otro caso podría prometer algo que la empresa no ofrece.
- **Las reglas evitan temas que no son de la empresa** (P9).
- **Desventaja de nuestra regla:** en P8 la regla hizo que el modelo respondiera "no tengo información" cuando sí podía decir "no tenemos de 100W, tenemos de 20W". Nuestra regla 2 es demasiado estricta para preguntas sobre productos que no existen. Una mejora sería agregar: "Si preguntan por un producto que no está en el catálogo, di que no lo vendemos y ofrece el más parecido del contexto".

---

## Experimento 3: recuperar 1 fragmento en vez de 4 (k=1)

| # | k=4 | k=1 |
|---|---|---|
| P5 | Recupera el producto **y** la sección 3 de la política. Dice que, como llegó vencido, sí tiene derecho a una solución. | Solo recupera el fragmento del producto (que dice "devolvible: no"). **Responde mal:** "no es posible procesar una devolución", sin mencionar la excepción para productos vencidos. |
| P6 | Respuesta correcta con la regla de los 5 días hábiles. | También correcta, porque el fragmento más parecido fue justo la sección "10. RETRASOS EN LA ENTREGA". |

### Qué aprendimos

- Con k=1 el prompt es más corto (unos 600 tokens en vez de 950), o sea más barato.
- Pero si la respuesta necesita dos documentos (el producto y la política), con un solo fragmento falta información y el modelo responde mal. P5 pasó de una respuesta correcta a una que le niega al cliente algo a lo que tiene derecho.
- Por eso dejamos **k=4**: la diferencia de costo es de fracciones de centavo y evita este tipo de errores.

---

## Conclusión

1. El RAG es lo que más mejora las respuestas. Sin RAG, DeepSeek Flash inventó datos en 7 de 10 preguntas. Con RAG respondió bien 9 de 10 y supo decir "no tengo información" cuando correspondía.
2. El prompt sigue siendo importante: las reglas controlan el largo, el formato y que el modelo no complete con suposiciones.
3. La calidad de la búsqueda (modelo de embeddings y k) limita todo el sistema. El error que quedó (P5) no fue del LLM, fue de la búsqueda.
4. El costo fue muy bajo: 0.0069 USD por 25 llamadas. Esto confirma la elección de DeepSeek Flash por su relación costo/calidad/beneficio para un piloto.
