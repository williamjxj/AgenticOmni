from fastapi import APIRouter
from backend.src.document_intel.ocr_service import OcrService
from backend.src.document_intel.table_extractor import TableExtractor

router = APIRouter()

@router.post("/api/document-intel/ocr")
def ocr_endpoint(file_path: str):
    ocr = OcrService()
    text = ocr.extract_text(file_path)
    return {"text": text}

@router.post("/api/document-intel/tables")
def tables_endpoint(file_path: str):
    extractor = TableExtractor()
    tables = extractor.extract_tables(file_path)
    return {"tables": tables}
