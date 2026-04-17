from src.openai_client.client import client
import json


def extract_financing_purpose(
    source_document: str, comparison_target_document: str
) -> dict:
    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=[
            {
                "role": "developer",
                "content": (
                    "You extract financing purpose from documents. "
                    "Return ONLY valid JSON with keys 'Expected Value' and 'Actual Value'. "
                    "Values should describe the purpose of financing (e.g., working capital, expansion, equipment purchase)."
                ),
            },
            {
                "role": "user",
                "content": f"""
SOURCE DOCUMENT:
{source_document}

COMPARISON TARGET DOCUMENT:
{comparison_target_document}

Extract:
- Expected Value (purpose of financing from source_document)
- Actual Value (purpose of financing from comparison_target_document)

Return strictly in JSON format:
{{
  "Expected Value": "...",
  "Actual Value": "..."
}}
""",
            },
        ],
        response_format={"type": "json_object"},
        temperature=0,
    )

    content = response.choices[0].message.content
    return json.loads(content)
