"""Asistente de EcoMarket con RAG (LangChain + ChromaDB + DeepSeek Flash).

Flujo de una pregunta:
1. Si el mensaje trae un número ECM-XXXX, se buscan los datos del pedido (como en el Taller 1).
2. La pregunta se convierte en vector y se buscan los K fragmentos más parecidos en Chroma.
3. Los fragmentos y los datos del pedido se ponen dentro del prompt.
4. La cadena prompt | modelo | parser genera la respuesta.

Ejemplos:
    python rag_chat.py --pregunta "¿Cuánto tarda el reembolso si pagué con PSE?"
    python rag_chat.py --pregunta "Quiero devolver mi pedido ECM-1005" --modo ambos
    python rag_chat.py --pregunta "¿Tienen tiendas físicas?" --solo-recuperar
    python rag_chat.py --interactivo
"""
import argparse
from dataclasses import dataclass, field

from langchain_core.documents import Document
from langchain_openai import ChatOpenAI

import config
from indexar import abrir_base_vectorial
from pedidos_tool import detectar_tracking, pedido_a_contexto
from prompts import PROMPT_RAG, PROMPT_RAG_SIN_REGLAS, PROMPT_SIN_RAG

PROMPTS = {
    "sin_rag": PROMPT_SIN_RAG,
    "rag": PROMPT_RAG,
    "rag_sin_reglas": PROMPT_RAG_SIN_REGLAS,
}

# Precios de deepseek-flash en USD por millón de tokens (hora pico, el caso más caro).
# Fuente: https://api-docs.deepseek.com/quick_start/pricing (consultado el 2026-10-16)
PRECIO_ENTRADA_USD = 0.30
PRECIO_SALIDA_USD = 1.20


@dataclass
class Resultado:
    respuesta: str
    fragmentos: list[tuple[Document, float]] = field(default_factory=list)
    tokens_entrada: int = 0
    tokens_salida: int = 0

    @property
    def costo_usd(self) -> float:
        return (self.tokens_entrada * PRECIO_ENTRADA_USD + self.tokens_salida * PRECIO_SALIDA_USD) / 1_000_000


def crear_llm() -> ChatOpenAI:
    if not config.DEEPSEEK_API_KEY:
        raise SystemExit("Falta DEEPSEEK_API_KEY. Copia .env.example a .env y pon tu API key.")
    # DeepSeek usa el mismo formato de API que OpenAI, por eso sirve la clase ChatOpenAI.
    return ChatOpenAI(
        model=config.MODELO_LLM,
        api_key=config.DEEPSEEK_API_KEY,
        base_url=config.DEEPSEEK_BASE_URL,
        temperature=config.TEMPERATURA,
        max_tokens=config.MAX_TOKENS_RESPUESTA,
        # deepseek-flash "piensa" antes de responder por defecto. Esos tokens se cobran,
        # y para respuestas cortas de soporte no hacen falta, así que se apaga.
        extra_body={"thinking": {"type": "disabled"}},
    )


def recuperar(base_vectorial, pregunta: str, k: int) -> list[tuple[Document, float]]:
    """Devuelve los k fragmentos más parecidos a la pregunta con su distancia coseno (menor = más parecido)."""
    return base_vectorial.similarity_search_with_score(pregunta, k=k)


def formatear_fragmentos(fragmentos: list[tuple[Document, float]]) -> str:
    if not fragmentos:
        return "(sin documentos)"
    bloques = []
    for i, (doc, _distancia) in enumerate(fragmentos, start=1):
        bloques.append(f"[Documento {i} - fuente: {doc.metadata['fuente']}]\n{doc.page_content}")
    return "\n\n".join(bloques)


class AsistenteEcoMarket:
    def __init__(self, k: int = config.K_FRAGMENTOS, usar_llm: bool = True):
        self.k = k
        self.base_vectorial = abrir_base_vectorial()
        self.llm = crear_llm() if usar_llm else None

    def responder(self, pregunta: str, modo: str = "rag", tracking: str | None = None) -> Resultado:
        tracking = tracking or detectar_tracking(pregunta)
        contexto_pedido = pedido_a_contexto(tracking)

        fragmentos = [] if modo == "sin_rag" else recuperar(self.base_vectorial, pregunta, self.k)

        # La cadena de LangChain: el prompt se llena con las variables y pasa al modelo
        cadena = PROMPTS[modo] | self.llm
        mensaje = cadena.invoke(
            {
                "pregunta": pregunta,
                "contexto_pedido": contexto_pedido,
                "contexto_documentos": formatear_fragmentos(fragmentos),
            }
        )
        uso = mensaje.usage_metadata or {}
        return Resultado(
            respuesta=mensaje.content.strip(),
            fragmentos=fragmentos,
            tokens_entrada=uso.get("input_tokens", 0),
            tokens_salida=uso.get("output_tokens", 0),
        )


def imprimir_fragmentos(fragmentos: list[tuple[Document, float]]):
    for doc, distancia in fragmentos:
        primera_linea = doc.page_content.splitlines()[0]
        print(f"  - distancia {distancia:.3f} | {doc.metadata['fuente']} | {primera_linea[:70]}")


def main():
    parser = argparse.ArgumentParser(description="Asistente de EcoMarket con RAG")
    parser.add_argument("--pregunta", help="Mensaje del cliente")
    parser.add_argument("--tracking", help="Número de seguimiento (opcional, también se detecta en el mensaje)")
    parser.add_argument("--modo", choices=["rag", "sin_rag", "rag_sin_reglas", "ambos"], default="rag")
    parser.add_argument("--k", type=int, default=config.K_FRAGMENTOS, help="Fragmentos a recuperar")
    parser.add_argument("--solo-recuperar", action="store_true", help="Solo muestra los fragmentos, no llama al modelo")
    parser.add_argument("--interactivo", action="store_true", help="Modo chat en la terminal")
    args = parser.parse_args()

    if not args.pregunta and not args.interactivo:
        parser.error("Usa --pregunta \"...\" o --interactivo")

    asistente = AsistenteEcoMarket(k=args.k, usar_llm=not args.solo_recuperar)

    if args.solo_recuperar:
        print(f"Fragmentos recuperados para: {args.pregunta}")
        imprimir_fragmentos(recuperar(asistente.base_vectorial, args.pregunta, args.k))
        return

    if args.interactivo:
        print("Asistente EcoMarket (RAG). Escribe 'salir' para terminar.")
        while True:
            pregunta = input("\nCliente: ").strip()
            if pregunta.lower() in {"salir", "exit", ""}:
                break
            resultado = asistente.responder(pregunta, modo="rag")
            print(f"EcoMarket: {resultado.respuesta}")
        return

    modos = ["sin_rag", "rag"] if args.modo == "ambos" else [args.modo]
    for modo in modos:
        resultado = asistente.responder(args.pregunta, modo=modo, tracking=args.tracking)
        print("=" * 80)
        print(f"MODO: {modo}")
        if resultado.fragmentos:
            print("Fragmentos usados:")
            imprimir_fragmentos(resultado.fragmentos)
        print("-" * 80)
        print(resultado.respuesta)
        print(
            f"\n(tokens entrada: {resultado.tokens_entrada}, salida: {resultado.tokens_salida}, "
            f"costo aprox: {resultado.costo_usd:.6f} USD)"
        )


if __name__ == "__main__":
    main()
