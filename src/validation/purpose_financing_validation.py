from src.openai_client.client import client
import json
import hashlib

SYSTEM_PROMPT = (
    "You extract financing purpose from documents. "
    "Return ONLY valid JSON with keys 'Expected Value' and 'Actual Value'. "
    "Values should describe the purpose of financing as it is written in the documents without any modification or formatting. "
)

USER_TEMPLATE = """
Extract:
- Expected Value (purpose of financing from source_document)
- Actual Value (purpose of financing from comparison_target_document)

Return strictly in JSON format:
{
  "Expected Value": "...",
  "Actual Value": "..."
}
"""


def extract_financing_purpose(
    source_document: str, comparison_target_document: str
) -> dict:
    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=[
            {"role": "developer", "content": SYSTEM_PROMPT},  # ✅ cacheable
            {"role": "user", "content": USER_TEMPLATE},  # ✅ cacheable
            {
                "role": "user",
                "content": f"SOURCE DOCUMENT:\n{source_document}\n\nCOMPARISON TARGET DOCUMENT:\n{comparison_target_document}",
            },  # ❌ dynamic (expected)
        ],
        response_format={"type": "json_object"},
        temperature=0,
        prompt_cache_key="financing-purpose-v1",
        prompt_cache_retention="24h",
    )

    return json.loads(response.choices[0].message.content)
