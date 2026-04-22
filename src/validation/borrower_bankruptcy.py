from src.openai_client.client import client
import json
import logging
import base64

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a strict OCR engine.

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


USER_TEMPLATE = """
Return strictly in JSON format:
{
  "is_borrower_bankruptcy": true/false,
  "has_proof_of_debt_general_form": true/false,
  "matched_text_borrower_bankruptcy": "<exact text snippet or empty string>",
  "matched_text_proof_of_debt": "<exact text snippet or empty string>"
}

Rules:
- Set "is_borrower_bankruptcy" to true ONLY if text explicitly contains terms like "Bankruptcy", "Bankrupt", or "Bankruptcy Proceedings".
- Set "has_proof_of_debt_general_form" to true ONLY if text explicitly contains "Proof of Debt" or "Proof of Debt General Form".
- Copy exact matching phrases into the corresponding "matched_text" fields.
- Do NOT infer meaning.
- Do NOT rephrase text.
- If no match, return empty string for that field.
"""


def validate_borrower_bankruptcy(image_path) -> dict:
    base64_image = encode_image(image_path)
    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=[
            {"role": "developer", "content": SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    },
                    {
                        "type": "text",
                        "text": USER_TEMPLATE,
                    },
                ],
            },
        ],
        temperature=0,
        response_format={"type": "json_object"},
        prompt_cache_key="borrower-bankruptcy-v1",  # 🔑 important
        prompt_cache_retention="24h",  # optional but powerful
    )

    result = json.loads(response.choices[0].message.content)
    return result
