from src.openai_client.client import client
import json

SYSTEM_PROMPT = (
    "You extract financial amounts from documents. "
    "Return ONLY valid JSON with keys 'Expected Value' and 'Actual Value'. "
    "Expected Value must be the facility amount from the source document. "
    "Actual Value must be the Debit/Debit RM value from Disbursement/Pengeluaran in the comparison target document. "
    "Do not modify, reformat, or calculate values. Extract exactly as written."
)

USER_TEMPLATE = """
Extract:
- Expected Value (facility amount from source_document)
- Actual Value (Debit/Debit RM value of Disbursement/Pengeluaran from comparison_target_document)

Return strictly in JSON format:
{
  "Expected Value": "...",
  "Actual Value": "..."
}
"""


def extract_facility_amount(
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
        prompt_cache_key="facility-amount-v1",
        prompt_cache_retention="24h",
    )

    json_content = json.loads(response.choices[0].message.content)
    json_content["Expected Value"] = (
        "The Facility Amount in Letter Offer is: "
        + json_content["Expected Value"].strip()
    )
    json_content["Actual Value"] = (
        "The Facility Amount in Loan Account Statement is: "
        + json_content["Actual Value"].strip()
    )

    return json_content
