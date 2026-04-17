from src.openai_client.client import client
import json


def extract_interest_rate(
    source_document: str, comparison_target_document: str
) -> dict:
    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=[
            {
                "role": "developer",
                "content": (
                    "You extract financial values from documents. "
                    "Return ONLY valid JSON with keys 'Expected Value' and 'Actual Value'. "
                    "Values should be interest/profit rates if found."
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
- Expected Value (from source_document)
- Actual Value (from comparison_target_document)

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
