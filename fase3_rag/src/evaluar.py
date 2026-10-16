"""Corre los experimentos del taller y guarda todas las respuestas en resultados/resultados_experimentos.md.

Experimentos:
1. Sin RAG vs con RAG: las 10 preguntas de prueba con los dos modos.
2. Cambio de prompt: 3 preguntas con el prompt RAG sin reglas (rag_sin_reglas).
3. Cambio de k: 2 preguntas con k=1 en lugar de k=4.

Son 25 llamadas a DeepSeek. Con respuestas de máximo 300 tokens el costo es de centavos de dólar.
    python evaluar.py
"""
from datetime import datetime

import config
from rag_chat import AsistenteEcoMarket, Resultado

PREGUNTAS = [
    ("P1", "Política", "¿Cuánto tarda el reembolso si pagué con PSE?"),
    ("P2", "Catálogo", "¿Cuánto cuesta el panel solar y cuántos tienen disponibles?"),
    ("P3", "FAQ", "¿Tienen algún programa de puntos o descuentos?"),
    ("P4", "Pedido + política", "Quiero devolver mi pedido ECM-1005, el panel no me sirvió. ¿Cómo hago?"),
    ("P5", "Pedido + política", "Me llegó el pedido ECM-1003 y los snacks estaban vencidos. ¿Qué puedo hacer?"),
    ("P6", "Pedido + política", "Mi pedido ECM-1004 está retrasado. ¿Lo puedo cancelar?"),
    ("P7", "Política", "¿Hacen envíos a México?"),
    ("P8", "No está en la base", "¿Venden paneles solares de 100W?"),
    ("P9", "Fuera de tema", "¿Cuál es la capital de Francia?"),
    ("P10", "Pedido sin número", "¿Dónde está mi pedido?"),
]

PREGUNTAS_CAMBIO_PROMPT = ["P5", "P8", "P9"]
PREGUNTAS_CAMBIO_K = ["P5", "P6"]


def bloque(titulo: str, resultado: Resultado) -> str:
    lineas = [f"**{titulo}**", ""]
    if resultado.fragmentos:
        lineas.append("Fragmentos recuperados (distancia coseno, menor = más parecido):")
        for doc, distancia in resultado.fragmentos:
            lineas.append(f"- `{distancia:.3f}` {doc.metadata['fuente']} → {doc.page_content.splitlines()[0][:70]}")
        lineas.append("")
    lineas.append(f"> {resultado.respuesta}")
    lineas.append("")
    lineas.append(f"_Tokens: {resultado.tokens_entrada} de entrada, {resultado.tokens_salida} de salida._")
    lineas.append("")
    return "\n".join(lineas)


def main():
    config.RESULTADOS_DIR.mkdir(exist_ok=True)
    asistente_k4 = AsistenteEcoMarket(k=4)
    asistente_k1 = AsistenteEcoMarket(k=1)
    preguntas = {pid: (tipo, texto) for pid, tipo, texto in PREGUNTAS}

    salida = [
        "# Resultados de los experimentos",
        "",
        f"Generado por `src/evaluar.py` el {datetime.now():%Y-%m-%d %H:%M}. "
        f"Modelo: `{config.MODELO_LLM}`, embeddings: `{config.MODELO_EMBEDDINGS}`, temperatura {config.TEMPERATURA}.",
        "",
    ]
    todos: list[Resultado] = []

    salida += ["## Experimento 1: sin RAG vs con RAG (k=4)", ""]
    for pid, tipo, texto in PREGUNTAS:
        print(f"Experimento 1 - {pid}")
        sin_rag = asistente_k4.responder(texto, modo="sin_rag")
        con_rag = asistente_k4.responder(texto, modo="rag")
        todos += [sin_rag, con_rag]
        salida += [f"### {pid} ({tipo}): {texto}", "", bloque("Sin RAG", sin_rag), bloque("Con RAG", con_rag)]

    salida += ["## Experimento 2: prompt RAG sin reglas", ""]
    for pid in PREGUNTAS_CAMBIO_PROMPT:
        print(f"Experimento 2 - {pid}")
        tipo, texto = preguntas[pid]
        resultado = asistente_k4.responder(texto, modo="rag_sin_reglas")
        todos.append(resultado)
        salida += [f"### {pid} ({tipo}): {texto}", "", bloque("RAG sin reglas", resultado)]

    salida += ["## Experimento 3: recuperar solo 1 fragmento (k=1)", ""]
    for pid in PREGUNTAS_CAMBIO_K:
        print(f"Experimento 3 - {pid}")
        tipo, texto = preguntas[pid]
        resultado = asistente_k1.responder(texto, modo="rag")
        todos.append(resultado)
        salida += [f"### {pid} ({tipo}): {texto}", "", bloque("Con RAG, k=1", resultado)]

    tokens_entrada = sum(r.tokens_entrada for r in todos)
    tokens_salida = sum(r.tokens_salida for r in todos)
    costo = sum(r.costo_usd for r in todos)
    salida += [
        "## Consumo total",
        "",
        f"- Llamadas al modelo: {len(todos)}",
        f"- Tokens de entrada: {tokens_entrada}",
        f"- Tokens de salida: {tokens_salida}",
        f"- Costo aproximado (precio de hora pico): {costo:.4f} USD",
        "",
    ]

    ruta = config.RESULTADOS_DIR / "resultados_experimentos.md"
    ruta.write_text("\n".join(salida), encoding="utf-8")
    print(f"Resultados guardados en {ruta}. Costo aproximado: {costo:.4f} USD")


if __name__ == "__main__":
    main()
