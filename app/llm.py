import httpx
from openai import OpenAI

from app.config import settings


SYSTEM_PROMPT = """
You are an internal Corporate Knowledge Assistant.

Your job is to answer employee questions using ONLY the provided internal
company-policy context.

Rules:
1. Use only the supplied context. Do not use outside knowledge.
2. If the context does not contain enough information, say:
   "Maaf, saya tidak menemukan informasi yang cukup dalam kebijakan internal
   yang tersedia."
3. If the question is unrelated to internal company policies, say:
   "Maaf, saya hanya bisa menjawab terkait kebijakan internal perusahaan."
4. Do not invent policy numbers, dates, amounts, eligibility rules, or procedures.
5. When possible, mention the document source in the answer.
6. Answer clearly and concisely in the same language as the user.
""".strip()


def build_context(matches: list[dict]) -> str:
    parts = []

    for i, match in enumerate(matches, start=1):
        parts.append(
            f"[Source {i}: {match['source']}, chunk {match['chunk_index']}]\n"
            f"{match['text']}"
        )

    return "\n\n".join(parts)


def generate_answer(question: str, matches: list[dict]) -> str:
    context = build_context(matches)

    user_prompt = f"""
Internal policy context:
{context}

Employee question:
{question}

Answer based strictly on the context above.
""".strip()

    if settings.llm_provider.lower() == "ollama":
        return _generate_ollama(user_prompt)

    return _generate_openai(user_prompt)


def _generate_openai(user_prompt: str) -> str:
    if not settings.openai_api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing. Add it to .env or use LLM_PROVIDER=ollama."
        )

    client = OpenAI(api_key=settings.openai_api_key)

    response = client.responses.create(
        model=settings.openai_model,
        instructions=SYSTEM_PROMPT,
        input=user_prompt,
    )

    return response.output_text.strip()


def _generate_ollama(user_prompt: str) -> str:
    payload = {
        "model": settings.ollama_model,
        "system": SYSTEM_PROMPT,
        "prompt": user_prompt,
        "stream": False,
    }

    response = httpx.post(
        f"{settings.ollama_base_url.rstrip('/')}/api/generate",
        json=payload,
        timeout=120,
    )
    response.raise_for_status()

    return response.json()["response"].strip()
