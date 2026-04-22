from src.openai_client.client import client
import json
import logging
import base64

logger = logging.getLogger(__name__)

PROMPT = """You are a strict OCR engine.

Rules:
- Extract ONLY text that is explicitly visible in the image.
- Do NOT infer, guess, complete, or correct text.
- Do NOT add punctuation, formatting, or missing words.
- Do NOT describe the image.
- Do NOT explain anything.
- If a word is unclear, output [UNCERTAIN].
- Preserve exact casing, spacing, and line breaks.
- Output ONLY the extracted text.
- If no text is visible, output: [NO_TEXT]

Violation of any rule is an error.
"""


def encode_image(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def security_party_letter_offer(image_path: str):
    base64_image = encode_image(image_path)

    messages = [
        {"role": "developer", "content": PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                },
                {
                    "type": "text",
                    "text": "Extract the details of SECURITY PARTY from the given image",
                },
            ],
        },
    ]

    completion = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=messages,
        temperature=0,
        prompt_cache_key="ocr-v2",  # 🔑 important for caching
        prompt_cache_retention="24h",
    )

    return completion.choices[0].message.content.strip()


def defendents_legal_document(image_path: str):
    base64_image = encode_image(image_path)

    messages = [
        {"role": "developer", "content": PROMPT},
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                },
                {
                    "type": "text",
                    "text": "Extract the details of Defendents from the given image",
                },
            ],
        },
    ]

    completion = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=messages,
        temperature=0,
        prompt_cache_key="ocr-v3",  # 🔑 important for caching
        prompt_cache_retention="24h",
    )

    return completion.choices[0].message.content.strip()


SYSTEM_PROMPT = """Your task is to:
1. Count the number of security partners in the source document under "9. (b) SECURITY PARTY".
2. Count the number of defendants in the target document.

Then apply this rule strictly:
- If the counts are equal → Matched = True
- If the counts are not equal → Matched = False

Do NOT contradict the counts. The boolean must follow the rule exactly.
Do NOT consider names, only counts."""


USER_TEMPLATE = """
Return strictly in JSON format:
{
  "security_partners_count": <number>,
  "defendants_count": <number>,
  "Matched": true/false,
  "Comments": "..."
}
"""


def get_legal_scoring(source_document: str, comparison_target_document: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=[
            {"role": "developer", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_TEMPLATE},  # static → cacheable
            {
                "role": "user",
                "content": f"SOURCE DOCUMENT:\n{source_document}\n\nTARGET DOCUMENT:\n{comparison_target_document}",
            },  # dynamic → not cached
        ],
        temperature=0,
        response_format={"type": "json_object"},
        prompt_cache_key="legal-scoring-v1",  # 🔑 important
        prompt_cache_retention="24h",  # optional but powerful
    )

    result = json.loads(response.choices[0].message.content)

    result["Matched"] = result["security_partners_count"] == result["defendants_count"]

    return result
