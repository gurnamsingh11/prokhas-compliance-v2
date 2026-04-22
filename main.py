from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import uuid
from src.workflow.core import orchestrate_workflow, process_borrower_bankruptcy

app = FastAPI(title="Workflow Validation API")

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)


def save_upload(file: UploadFile) -> str:
    file_ext = file.filename.split(".")[-1]
    temp_filename = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, temp_filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return file_path


@app.post("/validate/{workflow_name}")
def validate(
    workflow_name: str,
    source_pdf: UploadFile = File(...),
    target_pdf: UploadFile = File(...),
):
    try:
        # Save uploaded files
        source_path = save_upload(source_pdf)
        target_path = save_upload(target_pdf)

        # Run workflow
        result = orchestrate_workflow(
            workflow=workflow_name,
            source_pdf=source_path,
            target_pdf=target_path,
        )

        # Cleanup (important)
        os.remove(source_path)
        os.remove(target_path)

        return {"status": "success", "workflow": workflow_name, "result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/scenario_2")
def scenario_2(
    source_pdf: UploadFile = File(...),
    target_pdf: UploadFile = File(...),
):
    source_path = target_path = None

    try:
        # -------------------------------
        # Save uploaded files
        # -------------------------------
        source_path = save_upload(source_pdf)
        target_path = save_upload(target_pdf)

        # -------------------------------
        # Run Scenario 2 logic
        # -------------------------------
        result = process_borrower_bankruptcy(
            letter_of_offer_path=source_path,
            legal_document_path=target_path,
        )

        return {
            "status": "success",
            "scenario": "scenario_2",
            "result": result,
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        # -------------------------------
        # Cleanup (always runs)
        # -------------------------------
        try:
            if source_path and os.path.exists(source_path):
                os.remove(source_path)
            if target_path and os.path.exists(target_path):
                os.remove(target_path)
        except Exception as cleanup_error:
            raise HTTPException(status_code=500, detail=str(cleanup_error))
