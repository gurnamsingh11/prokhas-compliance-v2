import logging
import base64
import json
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

Violation of any rule is an error.
"""

STRUCTURED_PROMPTS = {
    "repayment_history": """Extract only the repayment history section.

Rules:
- Return year labels as an ordered list
- Return month codes exactly as shown, in order
- Carefully Return (0's) values exactly as shown
- Do not reorder, group, or interpret any values
- Do not assume counts match or map months to years
- Return only valid JSON matching the schema
"""
}


def encode_image(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


def extract_text_from_image(image_path: str, target: str = None):
    base64_image = encode_image(image_path)

    # --- choose mode ---
    if target is None:
        messages = [
            {"role": "developer", "content": PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    }
                ],
            },
        ]

        completion = client.chat.completions.create(
            model="gpt-5.4-nano",
            messages=messages,
            temperature=0,
            prompt_cache_key="ocr-v1",
            prompt_cache_retention="24h",
        )

        return completion.choices[0].message.content.strip()

    # --- structured extraction mode ---
    if target == "repayment_history":
        messages = [
            {"role": "developer", "content": STRUCTURED_PROMPTS[target]},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
                    }
                ],
            },
        ]

        completion = client.chat.completions.create(
            model="gpt-5.4",
            messages=messages,
            temperature=0,
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "repayment_history",
                    "schema": {
                        "type": "object",
                        "properties": {
                            "repayment_history": {
                                "type": "object",
                                "properties": {
                                    "years": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "pattern": "^[0-9]{4}$",
                                        },
                                    },
                                    "months_sequence": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "minLength": 1,
                                            "maxLength": 1,
                                        },
                                    },
                                    "delinquency_pattern": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                    },
                                },
                                "required": [
                                    "years",
                                    "months_sequence",
                                    "delinquency_pattern",
                                ],
                                "additionalProperties": False,
                            }
                        },
                        "required": ["repayment_history"],
                        "additionalProperties": False,
                    },
                },
            },
        )

        return json.loads(completion.choices[0].message.content)

    raise ValueError(f"Unsupported target: {target}")
