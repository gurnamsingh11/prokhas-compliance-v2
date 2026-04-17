from src.pdf_img_extractor.extractor import pdf_to_images
from src.img_ocr.openai_ocr import extract_text_from_image
from src.validation.interest_profit_validation import extract_interest_rate
from src.validation.purpose_financing_validation import extract_financing_purpose
from src.config.config import settings, delete_directories_from_paths


import logging

logger = logging.getLogger(__name__)


def orchestrate_workflow(workflow, source_pdf, target_pdf, settings=settings):
    logger.info("Starting workflow: %s", workflow)

    workflow_map = {
        "interest_profit_validation": extract_interest_rate,
        "purpose_financing_validation": extract_financing_purpose,
    }

    if workflow not in workflow_map:
        logger.error("Unsupported workflow: %s", workflow)
        raise ValueError(f"Unsupported workflow: {workflow}")

    try:
        source_page_number = settings[workflow]["source"]
        target_page_number = settings[workflow]["target"]

        logger.debug(
            "Using pages - source: %s, target: %s",
            source_page_number,
            target_page_number,
        )

        source_path = pdf_to_images(source_pdf, page_number=source_page_number)
        comparison_path = pdf_to_images(target_pdf, page_number=target_page_number)

        logger.debug("Generated image paths: %s, %s", source_path, comparison_path)

        source_text = extract_text_from_image(source_path)
        comparison_text = extract_text_from_image(comparison_path)

        logger.debug("Extracted text from both documents")

        validation_func = workflow_map[workflow]
        validation = validation_func(source_text, comparison_text)

        logger.info("Validation result for %s: %s", workflow, validation)

        if validation:
            delete_directories_from_paths(source_path, comparison_path)
            logger.debug("Temporary directories cleaned up")

        return validation

    except Exception as e:
        logger.exception("Workflow %s failed: %s", workflow, str(e))
        raise
