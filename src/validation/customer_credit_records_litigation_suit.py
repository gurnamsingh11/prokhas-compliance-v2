from src.openai_client.client import client
import json

SYSTEM_PROMPT = (
    "You extract specific structured information from documents. "
    "Return ONLY valid JSON with keys 'Expected Value' and 'Actual Value'. "
    "Expected Value must be ONLY sub-point (a) under 'Customer's credit records and litigation / suit' from the source document. "
    "Actual Value must be the COMPLETE 'Conduct of account for last 12 months' section from the comparison target document. "
    "CRITICAL RULES FOR ACTUAL VALUE: "
    "- Include the year labels (e.g., 2021, 2020). "
    "- Include the month sequence (e.g., O S A J J M A M F J D N). "
    "- Include ALL corresponding 6-digit values. "
    "Do not summarize, interpret, or reformat."
)


USER_TEMPLATE = """
Extract:
- Expected Value (ONLY sub-point a) under "Customer's credit records and litigation / suit")
- Actual Value (FULL 'Conduct of account for last 12 months' boxed section including:
  - Year labels
  - Month sequence
  - All 6-digit values)

Return strictly in JSON format:
{
  "Expected Value": "...",
  "Actual Value": "..."
}
"""


def extract_credit_and_conduct(
    source_document: str, comparison_target_document: str
) -> dict:
    response = client.chat.completions.create(
        model="gpt-5.4-nano",
        messages=[
            {"role": "developer", "content": SYSTEM_PROMPT},  # cacheable
            {"role": "user", "content": USER_TEMPLATE},  # cacheable
            {
                "role": "user",
                "content": f"SOURCE DOCUMENT:\n{source_document}\n\nCOMPARISON TARGET DOCUMENT:\n{comparison_target_document}",
            },  # dynamic
        ],
        response_format={"type": "json_object"},
        temperature=0,
        prompt_cache_key="credit-conduct-v1",
        prompt_cache_retention="24h",
    )

    return json.loads(response.choices[0].message.content)
