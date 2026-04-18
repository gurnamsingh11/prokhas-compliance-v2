from src.openai_client.client import client
import json


SYSTEM_PROMPT = (
    "You extract financial values from documents. "
    "Return the values as it is without any modification or formatting . "
    "Return ONLY valid JSON with keys 'Expected Value' and 'Actual Value'. "
    "Values should be interest/profit rates if found."
)

USER_TEMPLATE = """
Extract:
- Expected Value (Interest / Profit Rate from source_document)
- Actual Value (Payment -> Installment calculation from comparison_target_document)

Return strictly in JSON format:
{
  "Expected Value": "...",
  "Actual Value": "..."
}
"""


def extract_interest_rate(
    source_document: str, comparison_target_document: str
) -> dict:
    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=[
            {"role": "developer", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_TEMPLATE},  # static → cacheable
            {
                "role": "user",
                "content": f"SOURCE DOCUMENT:\n{source_document}\n\nCOMPARISON TARGET DOCUMENT:\n{comparison_target_document}",
            },  # dynamic → not cached
        ],
        temperature=0,
        response_format={"type": "json_object"},
        prompt_cache_key="interest-rate-extraction-v1",  # 🔑 important
        prompt_cache_retention="24h",  # optional but powerful
    )

    return json.loads(response.choices[0].message.content)
