import os


DEFAULT_LLM_MODEL = "gpt-4o-mini"

SYSTEM_INSTRUCTION = (
    "You are a credit risk analyst assistant. Answer only using the provided "
    "scoring response, SHAP driver preview, human review context, and retrieved "
    "project documentation snippets. Do not invent applicant facts, policies, "
    "thresholds, or approval decisions. If the provided context is insufficient, "
    "say what is missing. Your answer is analyst decision support, not automated "
    "credit approval or rejection."
)


def get_default_llm_model():
    return os.getenv("OPENAI_MODEL", DEFAULT_LLM_MODEL)


def get_llm_config(model=None):
    return {
        "api_key": os.getenv("OPENAI_API_KEY"),
        "model": model or get_default_llm_model(),
    }


def build_llm_prompt(
    question,
    detected_intent,
    scoring_evidence,
    driver_preview,
    review_context_summary,
    retrieved_context,
    limitations,
    llm_style="analyst",
):
    return f"""
Answer the analyst question using only the context below.

Return a concise professional answer with these sections:
- Short answer
- Key evidence
- SHAP interpretation
- Human review / governance note
- Limitations

Style: {llm_style}

Question:
{question}

Detected intent:
{detected_intent}

Scoring evidence:
{scoring_evidence}

SHAP driver preview:
{driver_preview}

Human review context:
{review_context_summary}

Retrieved project documentation snippets:
{retrieved_context}

Known limitations:
{limitations}

Important boundaries:
- Use only the provided context.
- Do not invent applicant facts, policies, thresholds, or approval decisions.
- If information is missing, state what is missing.
- This is analyst decision support, not automated approval or rejection.
""".strip()


def generate_llm_answer(
    question,
    detected_intent,
    scoring_evidence,
    driver_preview,
    review_context_summary,
    retrieved_context,
    limitations,
    temperature=0.2,
    llm_style="analyst",
    model=None,
):
    config = get_llm_config(model=model)
    api_key = config["api_key"]
    model = config["model"]

    if not api_key:
        return {
            "llm_enabled": False,
            "llm_answer": None,
            "llm_model": model,
            "llm_warnings": [
                "OPENAI_API_KEY is not configured; deterministic answer was used."
            ],
        }

    try:
        from openai import OpenAI
    except ImportError:
        return {
            "llm_enabled": False,
            "llm_answer": None,
            "llm_model": model,
            "llm_warnings": [
                "The openai package is not installed; deterministic answer was used."
            ],
        }

    prompt = build_llm_prompt(
        question=question,
        detected_intent=detected_intent,
        scoring_evidence=scoring_evidence,
        driver_preview=driver_preview,
        review_context_summary=review_context_summary,
        retrieved_context=retrieved_context,
        limitations=limitations,
        llm_style=llm_style,
    )

    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model=model,
            temperature=temperature,
            messages=[
                {"role": "system", "content": SYSTEM_INSTRUCTION},
                {"role": "user", "content": prompt},
            ],
        )
        llm_answer = response.choices[0].message.content
    except Exception as exc:
        return {
            "llm_enabled": False,
            "llm_answer": None,
            "llm_model": model,
            "llm_warnings": [
                f"LLM call failed; deterministic answer was used. Error: {exc}"
            ],
        }

    if not llm_answer or not llm_answer.strip():
        return {
            "llm_enabled": False,
            "llm_answer": None,
            "llm_model": model,
            "llm_warnings": [
                "LLM returned an empty response; deterministic answer was used."
            ],
        }

    return {
        "llm_enabled": True,
        "llm_answer": llm_answer.strip(),
        "llm_model": model,
        "llm_warnings": [],
    }
