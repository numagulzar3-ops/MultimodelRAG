from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
import shutil

from backend.rag_engine import (
    answer_question,
    process_document
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Multimodal RAG API"
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# UPLOAD DIRECTORY
# ============================================================

UPLOAD_DIR = Path("uploads")

UPLOAD_DIR.mkdir(
    exist_ok=True
)


# ============================================================
# REQUEST MODEL
# ============================================================

class QuestionRequest(BaseModel):

    question: str


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Multimodal RAG API is running!"
    }


# ============================================================
# UPLOAD DOCUMENT
# ============================================================

@app.post("/upload")
async def upload_document(
    file: UploadFile = File(...)
):

    filename = file.filename or ""

    extension = Path(
        filename
    ).suffix.lower()


    # --------------------------------------------------------
    # Check file type
    # --------------------------------------------------------

    if extension not in [
        ".pdf",
        ".docx"
    ]:

        raise HTTPException(
            status_code=400,
            detail="Only PDF and DOCX files are supported."
        )


    # --------------------------------------------------------
    # Save file
    # --------------------------------------------------------

    file_path = UPLOAD_DIR / filename


    with open(
        file_path,
        "wb"
    ) as buffer:

        shutil.copyfileobj(
            file.file,
            buffer
        )


    # --------------------------------------------------------
    # Process document
    # --------------------------------------------------------

    try:

        result = process_document(
            str(file_path)
        )

    except Exception as error:

        print("ERROR IN /upload:")
        print(type(error).__name__)
        print(str(error))

        if file_path.exists():

            file_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )


    return {

        "message": "Document uploaded successfully.",

        "filename": filename,

        "chunks": result["chunks"],

        "vectors": result["vectors"]

    }


# ============================================================
# ASK QUESTION
# ============================================================

@app.post("/ask")
def ask_question(
    request: QuestionRequest
):

    try:

        result = answer_question(
            request.question
        )

        return {
            "question": request.question,
            "answer": result["answer"],
            "sources": result["sources"]
        }

    except Exception as error:

        # ----------------------------------------------------
        # IMPORTANT DEBUGGING LOG
        # ----------------------------------------------------

        print("\n========================================")
        print("ERROR IN /ask:")
        print("ERROR TYPE:", type(error).__name__)
        print("ERROR MESSAGE:", str(error))
        print("========================================\n")

        raise HTTPException(
            status_code=500,
            detail=str(error)
        )