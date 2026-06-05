import re
from pathlib import Path
from typing import Literal

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.analytics_service import REPORTS_DIR, generate_reports, list_reports
from app.schemas import ReportGenerateOut, ReportOut

router = APIRouter(prefix="/reports", tags=["reports"])

_FILENAME_RE = re.compile(r"^[a-z_]+\.(png|pdf)$")


@router.get("", response_model=list[ReportOut])
def get_reports():
    return list_reports()


@router.post("/generate", response_model=ReportGenerateOut)
def create_reports(fmt: Literal["png", "pdf"] = "png"):
    try:
        items = generate_reports(fmt)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Report generation failed: {exc}") from exc
    return ReportGenerateOut(format=fmt, items=items)


@router.get("/files/{filename}")
def download_report(filename: str):
    if not _FILENAME_RE.match(filename):
        raise HTTPException(status_code=400, detail="Invalid filename")

    path = (REPORTS_DIR / filename).resolve()
    if not str(path).startswith(str(REPORTS_DIR.resolve())):
        raise HTTPException(status_code=400, detail="Invalid filename")
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Report not found")

    media = "application/pdf" if path.suffix == ".pdf" else "image/png"
    return FileResponse(path, media_type=media, filename=path.name)
