import logging
import base64
from src.openai_client.client import client

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

Violation of any rule is an error."""


def encode_image(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


MESSAGES_TEMPLATE = [
    {
        "role": "developer",
        "content": PROMPT,  # static → cacheable
    }
]


def extract_text_from_image(image_path: str) -> str:
    base64_image = encode_image(image_path)

    messages = MESSAGES_TEMPLATE + [
        {
            "role": "user",
            "content": [
                {
                    "type": "image_url",
                    "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                }
            ],
        }
    ]

    completion = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=messages,
        temperature=0,
        prompt_cache_key="ocr-v1",
        prompt_cache_retention="24h",
    )

    return completion.choices[0].message.content.strip()
