# Resultados de los experimentos

Generado por `src/evaluar.py` el 2026-10-16 08:37. Modelo: `deepseek-flash`, embeddings: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, temperatura 0.0.

## Experimento 1: sin RAG vs con RAG (k=4)

### P1 (Política): ¿Cuánto tarda el reembolso si pagué con PSE?

**Sin RAG**

> Los reembolsos a pagos realizados con PSE suelen procesarse en un plazo de 5 a 10 días hábiles, dependiendo de tu banco. Una vez aprobado el reembolso, recibirás un correo de confirmación con el detalle. Si no ves el dinero después de ese tiempo, te recomendamos contactar a tu entidad bancaria.

_Tokens: 114 de entrada, 85 de salida._

**Con RAG**

Fragmentos recuperados (distancia coseno, menor = más parecido):
- `0.386` politica_devoluciones_y_envios.pdf → 7. REEMBOLSOS
- `0.493` politica_devoluciones_y_envios.pdf → 2. PLAZO PARA DEVOLVER UN PRODUCTO
- `0.582` preguntas_frecuentes.json → Pregunta: ¿Qué medios de pago aceptan?
- `0.588` preguntas_frecuentes.json → Pregunta: ¿Cómo pido factura electrónica?

> El reembolso a PSE se realiza entre 3 y 5 días hábiles después de que EcoMarket recibe y revisa el producto devuelto. Ten en cuenta que el costo del envío original solo se reembolsa si el producto llegó dañado, vencido o equivocado. Si quieres gestionar una devolución, necesito tu número de seguimiento en formato ECM-XXXX.

_Tokens: 855 de entrada, 91 de salida._

### P2 (Catálogo): ¿Cuánto cuesta el panel solar y cuántos tienen disponibles?

**Sin RAG**

> En EcoMarket tenemos paneles solares desde $1.200.000 COP, según la potencia y marca. Para confirmar disponibilidad exacta y precio actualizado, necesito que me indiques el modelo o la referencia que te interesa. También puedo ayudarte a revisar tu pedido si me compartes el número de seguimiento.

_Tokens: 112 de entrada, 72 de salida._

**Con RAG**

Fragmentos recuperados (distancia coseno, menor = más parecido):
- `0.291` catalogo_productos.csv → Producto: Panel solar portátil 20W (SKU ECO-005).
- `0.322` catalogo_productos.csv → Producto: Cargador solar para celular (SKU ECO-010).
- `0.600` catalogo_productos.csv → Producto: Bolsas de tela para mercado (x3) (SKU ECO-013).
- `0.625` catalogo_productos.csv → Producto: Set de contenedores de vidrio (SKU ECO-007).

> El Panel solar portátil 20W (SKU ECO-005) cuesta 289.000 COP y hay 14 unidades disponibles.

_Tokens: 879 de entrada, 30 de salida._

### P3 (FAQ): ¿Tienen algún programa de puntos o descuentos?

**Sin RAG**

> ¡Claro que sí! En EcoMarket contamos con un programa de puntos llamado EcoPuntos, donde acumulas 1 punto por cada $1.000 de compra y luego puedes canjearlos por descuentos en tus próximos pedidos. También ofrecemos descuentos especiales por temporada y para clientes frecuentes. Si quieres, puedo ayudarte a consultar tus puntos acumulados o los descuentos vigentes.

_Tokens: 108 de entrada, 97 de salida._

**Con RAG**

Fragmentos recuperados (distancia coseno, menor = más parecido):
- `0.577` preguntas_frecuentes.json → Pregunta: ¿Tienen un programa de puntos o descuentos?
- `0.642` preguntas_frecuentes.json → Pregunta: ¿Tienen tiendas físicas?
- `0.646` preguntas_frecuentes.json → Pregunta: ¿Puedo pagar en cuotas?
- `0.688` preguntas_frecuentes.json → Pregunta: ¿Qué medios de pago aceptan?

> Sí, contamos con el programa EcoPuntos: por cada 1.000 COP de compra recibes 1 EcoPunto, y con 100 EcoPuntos obtienes un descuento de 10.000 COP en tu siguiente compra. Ten en cuenta que los puntos vencen a los 12 meses.

_Tokens: 730 de entrada, 71 de salida._

### P4 (Pedido + política): Quiero devolver mi pedido ECM-1005, el panel no me sirvió. ¿Cómo hago?

**Sin RAG**

> Hola María Fernanda, lamento que el panel solar no te haya servido. Como tu pedido ECM-1005 fue entregado el 2 de septiembre y está dentro de la ventana de 30 días, puedes solicitar la devolución escribiéndonos por este mismo canal o al correo de servicio al cliente con tu número de seguimiento. Te enviaremos la guía de recogida y, una vez recibido el producto, procesaremos el reembolso. ¿Quieres que iniciemos el trámite ahora mismo?

_Tokens: 229 de entrada, 115 de salida._

**Con RAG**

Fragmentos recuperados (distancia coseno, menor = más parecido):
- `0.528` preguntas_frecuentes.json → Pregunta: ¿Cómo sé dónde está mi pedido?
- `0.528` politica_devoluciones_y_envios.pdf → 5. CÓMO SOLICITAR UNA DEVOLUCIÓN
- `0.605` politica_devoluciones_y_envios.pdf → 10. RETRASOS EN LA ENTREGA
- `0.627` catalogo_productos.csv → Producto: Panel solar portátil 20W (SKU ECO-005).

> Puedes solicitarla desde "Mis pedidos" en el sitio web o la aplicación, eligiendo el pedido ECM-1005 y haciendo clic en "Solicitar devolución" con el motivo. EcoMarket te enviará en máximo 2 días hábiles una guía de envío prepagada al correo, y luego entregas el paquete en cualquier punto de la transportadora indicada, sin costo para ti. Como tu pedido fue entregado el 2026-09-02 y es devolvible, aún estás dentro de la ventana de devolución de 30 días.

_Tokens: 966 de entrada, 132 de salida._

### P5 (Pedido + política): Me llegó el pedido ECM-1003 y los snacks estaban vencidos. ¿Qué puedo hacer?

**Sin RAG**

> Lamento mucho lo ocurrido con tu pedido ECM-1003, Ana. Como los snacks orgánicos son un producto perecedero, no admiten devolución por norma sanitaria, pero si llegaron vencidos podemos ayudarte con un reemplazo o reembolso. Te pido enviar una foto del empaque con la fecha de vencimiento visible para radicar el caso. Escríbenos a servicioalcliente@ecomarket.com.co y lo gestionamos de inmediato.

_Tokens: 237 de entrada, 110 de salida._

**Con RAG**

Fragmentos recuperados (distancia coseno, menor = más parecido):
- `0.529` catalogo_productos.csv → Producto: Snacks orgánicos (mix frutos secos) (SKU ECO-003).
- `0.589` preguntas_frecuentes.json → Pregunta: ¿Cómo sé dónde está mi pedido?
- `0.599` preguntas_frecuentes.json → Pregunta: ¿Qué pasa si un producto está agotado?
- `0.604` politica_devoluciones_y_envios.pdf → 3. PRODUCTOS QUE NO ADMITEN DEVOLUCIÓN

> Lamento lo ocurrido con tu pedido ECM-1003 de snacks orgánicos, que fue entregado el 13 de septiembre en Cali. Aunque los alimentos perecederos no admiten devolución por norma sanitaria, si el producto llegó vencido sí tienes derecho a una solución según la sección 6 de la política. Te recomiendo escribir al chat de la tienda con tu número de seguimiento ECM-1003 para que un agente gestione tu caso.

_Tokens: 1012 de entrada, 105 de salida._

### P6 (Pedido + política): Mi pedido ECM-1004 está retrasado. ¿Lo puedo cancelar?

**Sin RAG**

> Hola Jorge, lamento el retraso de tu pedido ECM-1004. Como aún no ha sido entregado, sí es posible cancelarlo; te sugiero confirmarlo pronto para evitar que salga a despacho. Si prefieres, también puedo ayudarte a hacer seguimiento con la transportadora. ¿Qué deseas hacer?

_Tokens: 219 de entrada, 72 de salida._

**Con RAG**

Fragmentos recuperados (distancia coseno, menor = más parecido):
- `0.398` politica_devoluciones_y_envios.pdf → 10. RETRASOS EN LA ENTREGA
- `0.514` preguntas_frecuentes.json → Pregunta: ¿Cómo sé dónde está mi pedido?
- `0.533` preguntas_frecuentes.json → Pregunta: ¿Cómo pido factura electrónica?
- `0.540` politica_devoluciones_y_envios.pdf → 5. CÓMO SOLICITAR UNA DEVOLUCIÓN

> Tu pedido ECM-1004 está retrasado por congestión en el centro de distribución regional y aún no ha sido entregado. Según la política, si el retraso supera 5 días hábiles después de la fecha estimada de entrega (2026-09-13), puedes solicitar la cancelación con reembolso completo, incluido el costo del envío. Te recomiendo confirmar con el chat de la tienda si ya se cumplieron esos 5 días hábiles para gestionar la cancelación.

_Tokens: 927 de entrada, 116 de salida._

### P7 (Política): ¿Hacen envíos a México?

**Sin RAG**

> ¡Hola! Por ahora EcoMarket realiza envíos únicamente dentro de Colombia, así que no tenemos cobertura para México. Si deseas, puedo ayudarte a revisar alternativas para tu pedido dentro del país. Gracias por escribirnos.

_Tokens: 106 de entrada, 55 de salida._

**Con RAG**

Fragmentos recuperados (distancia coseno, menor = más parecido):
- `0.535` preguntas_frecuentes.json → Pregunta: ¿Qué medios de pago aceptan?
- `0.545` politica_devoluciones_y_envios.pdf → 9. ENVÍOS
- `0.714` politica_devoluciones_y_envios.pdf → 1. ALCANCE
- `0.777` preguntas_frecuentes.json → Pregunta: ¿Cómo sé dónde está mi pedido?

> No, EcoMarket no hace envíos internacionales por ahora, así que no realizamos envíos a México. Si necesitas más ayuda, puedes escribir al chat de la tienda para que un agente te atienda.

_Tokens: 798 de entrada, 48 de salida._

### P8 (No está en la base): ¿Venden paneles solares de 100W?

**Sin RAG**

> ¡Hola! En EcoMarket sí contamos con paneles solares de 100W, ideales para proyectos pequeños y de bajo consumo. Te invito a revisar nuestra sección de energía solar en la tienda en línea para ver modelos y precios disponibles. Si necesitas ayuda para elegir el más adecuado, con gusto te asesoramos.

_Tokens: 108 de entrada, 75 de salida._

**Con RAG**

Fragmentos recuperados (distancia coseno, menor = más parecido):
- `0.336` catalogo_productos.csv → Producto: Panel solar portátil 20W (SKU ECO-005).
- `0.414` catalogo_productos.csv → Producto: Cargador solar para celular (SKU ECO-010).
- `0.671` catalogo_productos.csv → Producto: Set de contenedores de vidrio (SKU ECO-007).
- `0.694` catalogo_productos.csv → Producto: Bolsas de tela para mercado (x3) (SKU ECO-013).

> No tengo información sobre eso. Te recomiendo escribir al chat de la tienda para que un agente te ayude.

_Tokens: 875 de entrada, 26 de salida._

### P9 (Fuera de tema): ¿Cuál es la capital de Francia?

**Sin RAG**

> La capital de Francia es París. Si necesitas ayuda con tu pedido de EcoMarket, puedes darme tu número de seguimiento y con gusto te ayudo.

_Tokens: 105 de entrada, 35 de salida._

**Con RAG**

Fragmentos recuperados (distancia coseno, menor = más parecido):
- `0.770` politica_devoluciones_y_envios.pdf → 9. ENVÍOS
- `0.833` preguntas_frecuentes.json → Pregunta: ¿Qué medios de pago aceptan?
- `0.854` preguntas_frecuentes.json → Pregunta: ¿Cómo sé dónde está mi pedido?
- `0.958` politica_devoluciones_y_envios.pdf → 5. CÓMO SOLICITAR UNA DEVOLUCIÓN

> No tengo información sobre eso. Te recomiendo escribir al chat de la tienda para que un agente te ayude.

_Tokens: 877 de entrada, 26 de salida._

### P10 (Pedido sin número): ¿Dónde está mi pedido?

**Sin RAG**

> ¡Hola! Con gusto te ayudo a ubicar tu pedido, pero para consultarlo necesito que me compartas tu número de seguimiento o el correo con el que realizaste la compra. Una vez lo tenga, podré revisar el estado y la ubicación exacta de tu envío. Quedo atento para ayudarte lo antes posible.

_Tokens: 105 de entrada, 78 de salida._

**Con RAG**

Fragmentos recuperados (distancia coseno, menor = más parecido):
- `0.388` preguntas_frecuentes.json → Pregunta: ¿Cómo sé dónde está mi pedido?
- `0.517` preguntas_frecuentes.json → Pregunta: ¿Puedo cambiar la dirección de entrega después de comprar?
- `0.598` politica_devoluciones_y_envios.pdf → 5. CÓMO SOLICITAR UNA DEVOLUCIÓN
- `0.617` preguntas_frecuentes.json → Pregunta: ¿Necesito crear una cuenta para comprar?

> Para consultar el estado de tu pedido necesito tu número de seguimiento, que tiene el formato ECM-XXXX y llega a tu correo cuando haces la compra. También puedes verlo en la sección 'Mis pedidos'. ¿Me compartes tu número de seguimiento para ayudarte?

_Tokens: 781 de entrada, 64 de salida._

## Experimento 2: prompt RAG sin reglas

### P5 (Pedido + política): Me llegó el pedido ECM-1003 y los snacks estaban vencidos. ¿Qué puedo hacer?

**RAG sin reglas**

Fragmentos recuperados (distancia coseno, menor = más parecido):
- `0.529` catalogo_productos.csv → Producto: Snacks orgánicos (mix frutos secos) (SKU ECO-003).
- `0.589` preguntas_frecuentes.json → Pregunta: ¿Cómo sé dónde está mi pedido?
- `0.599` preguntas_frecuentes.json → Pregunta: ¿Qué pasa si un producto está agotado?
- `0.604` politica_devoluciones_y_envios.pdf → 3. PRODUCTOS QUE NO ADMITEN DEVOLUCIÓN

> Lamento mucho que hayas recibido tus snacks orgánicos vencidos, Ana. Tienes toda la razón en querer una solución, y quiero ayudarte con esto.

Aunque los alimentos perecederos como los snacks (mix de frutos secos) **no admiten devolución por norma sanitaria**, esto aplica cuando el producto llega en buen estado. En tu caso, al haber llegado **vencido**, sí tienes derecho a una solución, ya que la política de EcoMarket contempla excepciones cuando un producto no devolvible llega dañado, vencido o es diferente al pedido.

**¿Qué puedes hacer?**
1. **Reporta el problema cuanto antes**: escríbenos con tu número de seguimiento **ECM-1003** (que ya tenemos registrado) y, si puedes, adjunta una **foto del producto y de la fecha de vencimiento** visible en el empaque. Esto agiliza mucho la gestión.
2. **Solución disponible**: Al tratarse de un producto perecedero vencido, procede un **reemplazo del producto o el reembolso del valor pagado** (18.500 COP), según prefieras.

**Datos de tu pedido para referencia:**
- Producto: Snacks orgánicos (mix frutos secos) – SKU ECO-003
- Estado: Entregado el 2026-09-13 en Cali
- Valor: 18.500 COP

¿Quieres que gestione directamente tu caso para un **reemplazo** o prefieres el **reembolso**? Con tu confirmación y una foto del producto vencido, podemos avanzar de inmediato.

_Tokens: 707 de entrada, 375 de salida._

### P8 (No está en la base): ¿Venden paneles solares de 100W?

**RAG sin reglas**

Fragmentos recuperados (distancia coseno, menor = más parecido):
- `0.336` catalogo_productos.csv → Producto: Panel solar portátil 20W (SKU ECO-005).
- `0.414` catalogo_productos.csv → Producto: Cargador solar para celular (SKU ECO-010).
- `0.671` catalogo_productos.csv → Producto: Set de contenedores de vidrio (SKU ECO-007).
- `0.694` catalogo_productos.csv → Producto: Bolsas de tela para mercado (x3) (SKU ECO-013).

> Gracias por tu interés en nuestros productos. 😊

Revisando nuestro catálogo, actualmente **no tenemos paneles solares de 100W**. El panel solar que manejamos es el **Panel solar portátil 20W (SKU ECO-005)**, con las siguientes características:

- **Precio:** 289.000 COP
- **Stock:** 14 unidades disponibles
- **Descripción:** Panel solar plegable de 20W con salida USB, ideal para cargar celulares y baterías externas.
- **Materiales:** Silicio monocristalino y lona.
- **Cuidados:** No doblar las celdas y limpiar con un paño seco.
- **¿Se puede devolver?:** Sí.

Si necesitas más potencia, este modelo de 20W puede servirte para cargas básicas, aunque no alcanza la capacidad de un panel de 100W. Si quieres, puedo ayudarte a revisar otras alternativas o consultar si hay disponibilidad futura de modelos más potentes.

¿Te gustaría más información sobre el panel de 20W o sobre algún otro producto?

_Tokens: 570 de entrada, 251 de salida._

### P9 (Fuera de tema): ¿Cuál es la capital de Francia?

**RAG sin reglas**

Fragmentos recuperados (distancia coseno, menor = más parecido):
- `0.770` politica_devoluciones_y_envios.pdf → 9. ENVÍOS
- `0.833` preguntas_frecuentes.json → Pregunta: ¿Qué medios de pago aceptan?
- `0.854` preguntas_frecuentes.json → Pregunta: ¿Cómo sé dónde está mi pedido?
- `0.958` politica_devoluciones_y_envios.pdf → 5. CÓMO SOLICITAR UNA DEVOLUCIÓN

> La capital de Francia es **París**.

Si tu pregunta era sobre tu pedido o algún producto de EcoMarket, con gusto te ayudo; solo cuéntame qué necesitas. 😊

_Tokens: 572 de entrada, 40 de salida._

## Experimento 3: recuperar solo 1 fragmento (k=1)

### P5 (Pedido + política): Me llegó el pedido ECM-1003 y los snacks estaban vencidos. ¿Qué puedo hacer?

**Con RAG, k=1**

Fragmentos recuperados (distancia coseno, menor = más parecido):
- `0.529` catalogo_productos.csv → Producto: Snacks orgánicos (mix frutos secos) (SKU ECO-003).

> Lamento lo ocurrido con tu pedido ECM-1003 de Snacks orgánicos, entregado el 13 de septiembre de 2026 en Cali. Como es un producto de categoría alimentos perecederos, no admite devolución por norma sanitaria, así que no es posible procesar una devolución. Te recomiendo escribir al chat de la tienda para que un agente revise tu caso directamente.

_Tokens: 646 de entrada, 89 de salida._

### P6 (Pedido + política): Mi pedido ECM-1004 está retrasado. ¿Lo puedo cancelar?

**Con RAG, k=1**

Fragmentos recuperados (distancia coseno, menor = más parecido):
- `0.398` politica_devoluciones_y_envios.pdf → 10. RETRASOS EN LA ENTREGA

> Tu pedido ECM-1004 está retrasado por congestión en el centro de distribución regional, y según la política de EcoMarket solo puedes pedir la cancelación con reembolso completo, incluido el envío, si el retraso supera 5 días hábiles después de la fecha estimada de entrega, que era el 13 de septiembre de 2026. Como aún no se ha entregado, te recomiendo verificar si ya pasaron esos 5 días hábiles y, de ser así, solicitar la cancelación. Si necesitas confirmar el cálculo exacto o gestionar la cancelación, escribe al chat de la tienda para que un agente te ayude.

_Tokens: 589 de entrada, 153 de salida._

## Consumo total

- Llamadas al modelo: 25
- Tokens de entrada: 13227
- Tokens de salida: 2411
- Costo aproximado (precio de hora pico): 0.0069 USD
