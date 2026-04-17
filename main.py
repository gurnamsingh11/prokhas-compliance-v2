from fastapi import FastAPI, UploadFile, File, HTTPException
import shutil
import os
import uuid
from src.workflow.core import orchestrate_workflow

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
