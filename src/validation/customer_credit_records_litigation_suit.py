from src.openai_client.client import client
import json

SYSTEM_PROMPT = (
    "You extract specific structured information from documents. "
    "Return ONLY valid JSON with keys 'Expected Value' "
    "Expected Value must be ONLY sub-point (a) under 'Customer's credit records and litigation / suit' from the source document. "
    "Do not summarize, interpret, or reformat."
)


USER_TEMPLATE = """
Extract:
- Expected Value (ONLY sub-point a) under "Customer's credit records and litigation / suit")

Return strictly in JSON format:
{
  "Expected Value": "..."
}
"""


def extract_credit_and_conduct(source_document: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=[
            {"role": "developer", "content": SYSTEM_PROMPT},  # cacheable
            {"role": "user", "content": USER_TEMPLATE},  # cacheable
            {
                "role": "user",
                "content": f"SOURCE DOCUMENT:\n{source_document}",
            },  # dynamic
        ],
        response_format={"type": "json_object"},
        temperature=0,
        prompt_cache_key="credit-conduct-v1",
        prompt_cache_retention="24h",
    )

    return json.loads(response.choices[0].message.content)
