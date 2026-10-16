# Limitaciones y suposiciones

## Limitaciones de recursos

1. **Saldo limitado en la API de DeepSeek.** Usamos una cuenta propia con poco saldo. Por eso:
   - Corrimos solo 25 llamadas al modelo (10 preguntas en dos modos, más 5 de los otros experimentos).
   - Limitamos cada respuesta a 300 tokens y apagamos el modo "thinking".
   - Probamos el chunking y la búsqueda con `--solo-recuperar`, que no llama al modelo.
   Con más saldo haríamos más preguntas de prueba y repetiríamos cada una varias veces.

2. **Computador personal.** El modelo de embeddings corre en CPU en un portátil. Por eso escogimos un modelo pequeño (384 dimensiones). Un modelo más grande como `bge-m3` (~2.2 GB) también correría, pero más lento, y para 38 fragmentos no vimos necesidad.

3. **No tenemos documentos reales de una empresa.** EcoMarket es un caso de estudio. Los tres documentos (política, catálogo y preguntas frecuentes) los escribimos nosotros a partir de lo que tendría una tienda en línea. El PDF lo generamos desde un archivo de texto con LibreOffice (`data/fuentes/`).

## Suposiciones

1. **Los documentos están actualizados y no se contradicen.** El sistema responde con lo que dicen los documentos. Si la política cambia y nadie vuelve a indexar, el asistente da información vieja. En producción habría que volver a ejecutar `indexar.py` cada vez que cambie un documento.
2. **El número de pedido tiene el formato `ECM-XXXX`.** Si el cliente lo escribe distinto (por ejemplo "ECM 1004" o "1004"), no se detecta y el asistente le pide el número.
3. **No hay autenticación.** Cualquiera que escriba un número de pedido ve los datos de ese pedido. En producción habría que confirmar que el pedido es del cliente que pregunta.
4. **Una pregunta a la vez.** El asistente no recuerda los mensajes anteriores. Si el cliente da el número en un mensaje y pregunta en el siguiente, el segundo mensaje no tiene el número. Agregar memoria de conversación sería el siguiente paso.
5. **Pocos documentos.** Con 38 fragmentos, siempre pasar 4 al modelo funciona. Con miles de fragmentos habría que revisar si 4 es suficiente.
6. **Se pueden enviar los datos a DeepSeek.** La pregunta, el nombre del cliente, el producto y los fragmentos se envían a una API externa. Suponemos que esto es aceptable para un piloto con datos de prueba. Con datos reales habría que revisar la ley de protección de datos (en Colombia, la Ley 1581 de 2012) o usar un modelo local.

## Limitaciones del diseño que encontramos

1. **La búsqueda siempre trae 4 fragmentos, aunque ninguno sirva.** Para "¿Cuál es la capital de Francia?" Chroma igual devuelve 4 fragmentos (con distancias altas, de 0.77 a 0.96). Quien decide que no sirven es el LLM, siguiendo la regla del prompt. Una mejora sería descartar los fragmentos con distancia mayor a un límite (por ejemplo 0.7) antes de llamar al modelo; así ni siquiera se gastaría la llamada.
2. **El modelo de embeddings es pequeño.** Funciona bien para preguntas directas. Con preguntas muy indirectas o con errores de ortografía podría traer el fragmento equivocado.
3. **Temperatura 0 no garantiza la misma respuesta siempre.** Las respuestas son más estables, pero con la API pueden cambiar un poco entre ejecuciones. Por eso guardamos las respuestas reales en `resultados/`.
4. **No medimos con métricas automáticas.** Revisamos las respuestas a mano. Con más tiempo usaríamos métricas de RAG (por ejemplo, si la respuesta está apoyada en los fragmentos) sobre un conjunto de preguntas más grande.
