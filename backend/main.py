from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import tempfile, os
from extractor import extract_text_from_pdf
from rules import run_all_checks

app = FastAPI(title="Solar Permit Checker API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Solar Permit Checker API is running"}

@app.post("/check")
async def check_permit(file: UploadFile = File(...)):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Save uploaded file temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        contents = await file.read()
        tmp.write(contents)
        tmp_path = tmp.name

    try:
        # Extract text from PDF
        extracted = extract_text_from_pdf(tmp_path)

        # Run rule checks
        results = run_all_checks(extracted)

        return {
            "filename": file.filename,
            "pages_parsed": extracted["page_count"],
            "extracted_fields": extracted["fields"],
            "checks": results
        }
    finally:
        os.unlink(tmp_path)
