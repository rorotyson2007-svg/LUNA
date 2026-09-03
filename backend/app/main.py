import traceback

from fastapi import (
    FastAPI,
    HTTPException,
    UploadFile,
    File,
)

from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.pipeline import run_luna_pipeline

from app.ingestion.file_parser import (
    extract_text_from_file,
)


# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="LUNA",
    version="1.0.0",
    description=(
        "Law-enforcement Unified Network "
        "for Advanced Investigation"
    ),
)


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# MODELS
# ============================================================

class InvestigationRequest(BaseModel):
    case_text: str = ""


# ============================================================
# HEALTH
# ============================================================

@app.get("/")
async def root():

    return {
        "success": True,
        "name": "LUNA",
        "version": "1.0.0",
        "status": "ONLINE",
    }


@app.get("/health")
async def health():

    return {
        "success": True,
        "status": "ONLINE",
    }


# ============================================================
# GENERAL INVESTIGATION
# ============================================================

@app.post("/api/investigate")
async def investigate(
    request: InvestigationRequest,
):

    try:

        # ----------------------------------------------------
        # VALIDATE
        # ----------------------------------------------------

        case_text = (
            request.case_text or ""
        ).strip()

        if not case_text:

            raise HTTPException(
                status_code=400,
                detail="Case text cannot be empty.",
            )

        print(
            "LUNA: Investigation request received."
        )

        print(
            "LUNA: Case characters:",
            len(case_text),
        )

        # ----------------------------------------------------
        # RUN LUNA PIPELINE
        #
        # IMPORTANT:
        # run_luna_pipeline is ASYNC.
        # DO NOT use asyncio.to_thread().
        # ----------------------------------------------------

        result = await run_luna_pipeline(
            case_text=case_text,
        )

        # ----------------------------------------------------
        # VERIFY RESULT
        # ----------------------------------------------------

        if result is None:

            raise RuntimeError(
                "LUNA pipeline returned no result."
            )

        print(
            "LUNA: Pipeline result type:",
            type(result).__name__,
        )

        print(
            "LUNA: Sending result to frontend."
        )

        # ----------------------------------------------------
        # RETURN JSON RESULT
        # ----------------------------------------------------

        return result

    except HTTPException:

        raise

    except Exception as exc:

        print(
            "\n"
            "==================================================\n"
            "LUNA INVESTIGATION ERROR\n"
            "=================================================="
        )

        traceback.print_exc()

        print(
            "==================================================\n"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Investigation failed: "
                f"{type(exc).__name__}: "
                f"{str(exc)}"
            ),
        )


# ============================================================
# FILE EXTRACTION
# ============================================================

@app.post("/api/files/extract")
async def extract_file(
    file: UploadFile = File(...),
):

    try:

        # ----------------------------------------------------
        # VALIDATE FILE
        # ----------------------------------------------------

        if not file.filename:

            raise HTTPException(
                status_code=400,
                detail="No filename supplied.",
            )

        # ----------------------------------------------------
        # READ FILE
        # ----------------------------------------------------

        contents = await file.read()

        if not contents:

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        # ----------------------------------------------------
        # EXTRACT TEXT
        # ----------------------------------------------------

        text = extract_text_from_file(
            contents,
            file.filename,
        )

        if text is None:
            text = ""

        # ----------------------------------------------------
        # RESPONSE
        # ----------------------------------------------------

        return {
            "success": True,
            "filename": file.filename,
            "text": text,
            "characters": len(text),
        }

    except HTTPException:

        raise

    except Exception as exc:

        print(
            "\n"
            "==================================================\n"
            "LUNA FILE EXTRACTION ERROR\n"
            "=================================================="
        )

        traceback.print_exc()

        print(
            "==================================================\n"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "File extraction failed: "
                f"{type(exc).__name__}: "
                f"{str(exc)}"
            ),
        )