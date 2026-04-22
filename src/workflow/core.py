from src.pdf_img_extractor.extractor import pdf_to_images
from src.img_ocr.openai_ocr import extract_text_from_image
from src.validation.interest_profit_validation import extract_interest_rate
from src.validation.purpose_financing_validation import extract_financing_purpose
from src.validation.facility_amount_validation import extract_facility_amount
from src.validation.borrower_bankruptcy import validate_borrower_bankruptcy
from src.validation.legal_scoring import (
    get_legal_scoring,
    security_party_letter_offer,
    defendents_legal_document,
)
from src.validation.customer_credit_records_litigation_suit import (
    extract_credit_and_conduct,
)
from src.config.config import settings, delete_directories_from_paths
import logging

logger = logging.getLogger(__name__)


from concurrent.futures import ThreadPoolExecutor
import os


# -------------------------------
# Top-level helper functions
# -------------------------------


def extract_source_text(workflow, source_path):
    if workflow == "legal_scoring":
        return security_party_letter_offer(source_path)
    return extract_text_from_image(source_path)


def extract_target_text(workflow, comparison_path):
    if workflow == "legal_scoring":
        return defendents_legal_document(comparison_path)
    elif workflow == "customer_credit_records_validation":
        return extract_text_from_image(comparison_path, target="repayment_history")
    return extract_text_from_image(comparison_path)


# -------------------------------
# Main orchestrator
# -------------------------------


def orchestrate_workflow(workflow, source_pdf, target_pdf, settings=settings):
    logger.info("Starting workflow: %s", workflow)

    workflow_map = {
        "interest_profit_validation": extract_interest_rate,
        "purpose_financing_validation": extract_financing_purpose,
        "facility_amount_validation": extract_facility_amount,
        "customer_credit_records_validation": extract_credit_and_conduct,
        "legal_scoring": get_legal_scoring,
    }

    if workflow not in workflow_map:
        logger.error("Unsupported workflow: %s", workflow)
        raise ValueError(f"Unsupported workflow: {workflow}")

    source_path = comparison_path = bankruptcy_path = None

    try:
        config = settings[workflow]
        source_page_number = config["source"]
        target_page_number = config["target"]

        logger.debug(
            "Using pages - source: %s, target: %s",
            source_page_number,
            target_page_number,
        )

        # -------------------------------
        # STEP 1: Parallel PDF → Image
        # -------------------------------
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_source = executor.submit(
                pdf_to_images, source_pdf, page_number=source_page_number
            )
            future_target = executor.submit(
                pdf_to_images, target_pdf, page_number=target_page_number
            )

            source_path = future_source.result()
            comparison_path = future_target.result()

        logger.debug(
            "Generated image paths: %s, %s",
            source_path,
            comparison_path,
        )

        # -------------------------------
        # STEP 2: Parallel Text Extraction
        # -------------------------------
        with ThreadPoolExecutor(max_workers=2) as executor:
            future_src_text = executor.submit(
                extract_source_text, workflow, source_path
            )
            future_cmp_text = executor.submit(
                extract_target_text, workflow, comparison_path
            )

            source_text = future_src_text.result()
            comparison_text = future_cmp_text.result()

        logger.debug("Extracted text from both documents")

        # -------------------------------
        # STEP 3: Validation
        # -------------------------------
        validation_func = workflow_map[workflow]

        if workflow == "customer_credit_records_validation":
            validation = validation_func(source_text)
            validation["Actual Value"] = comparison_text["repayment_history"]
        else:
            validation = validation_func(source_text, comparison_text)

        logger.info("Validation result for %s: %s", workflow, validation)

        # -------------------------------
        # STEP 4: Bankruptcy fallback logic
        # -------------------------------
        if (
            workflow == "legal_scoring"
            and validation
            and not validation.get("result", {}).get("Matched", True)
        ):
            logger.info("Legal scoring failed → running borrower bankruptcy validation")

            bankruptcy_page = settings["borrower_bankruptcy_validation"]["source"]

            bankruptcy_path = pdf_to_images(target_pdf, page_number=bankruptcy_page)

            bankruptcy_result = validate_borrower_bankruptcy(bankruptcy_path)

            # Attach fallback result
            validation["borrower_bankruptcy_check"] = bankruptcy_result

            logger.info(
                "Borrower bankruptcy validation result: %s",
                bankruptcy_result,
            )

        return validation

    except Exception as e:
        logger.exception("Workflow %s failed: %s", workflow, str(e))
        raise

    finally:
        # -------------------------------
        # Cleanup
        # -------------------------------
        try:
            paths_to_clean = [
                p for p in [source_path, comparison_path, bankruptcy_path] if p
            ]
            if paths_to_clean:
                delete_directories_from_paths(*paths_to_clean)
                logger.debug("Temporary directories cleaned up")
        except Exception as cleanup_error:
            logger.warning("Cleanup failed: %s", cleanup_error)
