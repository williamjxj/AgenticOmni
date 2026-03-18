"""API routes for HuggingFace dataset import."""

from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from pydantic import BaseModel, Field

import structlog

from src.ingestion_parsing.tasks.hf_dataset_tasks import trigger_hf_dataset_import
from src.ingestion_parsing.services.hf_dataset_loader import HFDatasetLoader

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/datasets", tags=["datasets"])


class HFDatasetImportRequest(BaseModel):
    """Request model for HuggingFace dataset import."""
    
    dataset_name: str = Field(
        ...,
        description="HuggingFace dataset identifier (e.g., 'rajpurkar/squad')",
        examples=["rajpurkar/squad", "wikitext", "pubmed_qa"],
    )
    
    tenant_id: int = Field(
        ...,
        description="Tenant ID for data isolation",
        gt=0,
    )
    
    split: str = Field(
        default="train",
        description="Dataset split to import",
        examples=["train", "validation", "test"],
    )
    
    limit: int | None = Field(
        default=None,
        description="Maximum number of records to import (None = all)",
        gt=0,
        le=10000,
    )
    
    user_id: int | None = Field(
        default=None,
        description="User ID who initiated the import",
        gt=0,
    )


class HFDatasetImportResponse(BaseModel):
    """Response model for dataset import."""
    
    message: str = Field(
        ...,
        description="Status message",
    )
    
    job_id: str = Field(
        ...,
        description="Background job ID for tracking import progress",
    )
    
    dataset_name: str = Field(
        ...,
        description="Dataset identifier",
    )
    
    split: str = Field(
        ...,
        description="Dataset split being imported",
    )
    
    limit: int | None = Field(
        ...,
        description="Record limit",
    )


class DatasetValidationResponse(BaseModel):
    """Response model for dataset validation."""
    
    dataset_name: str = Field(
        ...,
        description="Dataset identifier",
    )
    
    accessible: bool = Field(
        ...,
        description="Whether the dataset is accessible",
    )
    
    message: str = Field(
        ...,
        description="Validation result message",
    )


@router.post(
    "/import",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=HFDatasetImportResponse,
    summary="Import HuggingFace Dataset",
    description="""
    Import a dataset from HuggingFace Hub into the RAG system.
    
    This endpoint triggers a background task that:
    1. Loads the dataset from HuggingFace
    2. Creates document records for each text entry
    3. Chunks the text using your existing 512-token chunker
    4. Generates embeddings and stores in pgvector
    
    **Supported Datasets:**
    - `rajpurkar/squad` - SQuAD QA dataset (contexts)
    - `pubmed_qa` - PubMed medical QA
    - `wikitext` - Wikipedia text
    - Any HuggingFace dataset with text content
    
    **Tips:**
    - Start with a small limit (100-500) for testing
    - Use tenant_id=1 for default tenant
    - The import runs in background via Dramatiq
    - Track progress using the returned job_id
    """,
)
async def import_huggingface_dataset(
    request: HFDatasetImportRequest,
) -> HFDatasetImportResponse:
    """Import a HuggingFace dataset into the RAG system.
    
    Args:
        request: Dataset import request
        
    Returns:
        Import response with job ID for tracking
        
    Raises:
        HTTPException 400: Invalid dataset name or parameters
        HTTPException 500: Import task failed to start
    """
    logger.info(
        "HuggingFace dataset import requested",
        dataset_name=request.dataset_name,
        tenant_id=request.tenant_id,
        split=request.split,
        limit=request.limit,
    )
    
    try:
        # Trigger background import task
        job_id = trigger_hf_dataset_import(
            dataset_name=request.dataset_name,
            tenant_id=request.tenant_id,
            split=request.split,
            limit=request.limit,
            user_id=request.user_id,
        )
        
        logger.info(
            "HuggingFace dataset import task triggered",
            job_id=job_id,
            dataset_name=request.dataset_name,
        )
        
        return HFDatasetImportResponse(
            message=f"Dataset import started. Processing {request.limit or 'all'} records from {request.dataset_name}.",
            job_id=job_id,
            dataset_name=request.dataset_name,
            split=request.split,
            limit=request.limit,
        )
        
    except Exception as e:
        logger.error(
            "Failed to trigger HuggingFace dataset import",
            dataset_name=request.dataset_name,
            error=str(e),
            error_type=type(e).__name__,
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start dataset import: {str(e)}",
        )


@router.get(
    "/validate/{dataset_name:path}",
    response_model=DatasetValidationResponse,
    summary="Validate Dataset Access",
    description="""
    Validate access to a HuggingFace dataset.
    
    Checks if:
    - The dataset exists on HuggingFace Hub
    - The dataset is accessible with current authentication
    - The dataset can be loaded
    
    Use this before importing to avoid errors.
    """,
)
async def validate_dataset_access(
    dataset_name: Annotated[
        str,
        Path(
            description="HuggingFace dataset identifier",
            examples=["rajpurkar/squad", "wikitext"],
        ),
    ],
) -> DatasetValidationResponse:
    """Validate access to a HuggingFace dataset.
    
    Args:
        dataset_name: HuggingFace dataset identifier
        
    Returns:
        Validation response with accessibility status
    """
    logger.info("Dataset validation requested", dataset_name=dataset_name)
    
    try:
        loader = HFDatasetLoader()
        accessible = loader.validate_dataset_access(dataset_name)
        
        if accessible:
            message = f"Dataset '{dataset_name}' is accessible and ready to import"
        else:
            message = f"Dataset '{dataset_name}' is not accessible. Check dataset name and authentication."
        
        return DatasetValidationResponse(
            dataset_name=dataset_name,
            accessible=accessible,
            message=message,
        )
        
    except Exception as e:
        logger.error(
            "Dataset validation error",
            dataset_name=dataset_name,
            error=str(e),
        )
        return DatasetValidationResponse(
            dataset_name=dataset_name,
            accessible=False,
            message=f"Validation error: {str(e)}",
        )


@router.get(
    "/supported",
    summary="List Supported Datasets",
    description="Get a list of commonly used datasets for document intelligence.",
)
async def list_supported_datasets() -> dict:
    """List supported and recommended HuggingFace datasets.
    
    Returns:
        Dictionary of supported datasets with descriptions
    """
    return {
        "supported_datasets": [
            {
                "name": "rajpurkar/squad",
                "description": "SQuAD - Stanford Question Answering Dataset",
                "use_case": "QA over documents",
                "size": "~18K training + 2K validation",
                "recommended_limit": 500,
            },
            {
                "name": "HuggingFaceM4/DocumentVQA",
                "description": "Document Visual Question Answering",
                "use_case": "Document visual QA",
                "size": "Varies",
                "recommended_limit": 100,
            },
            {
                "name": "pubmed_qa",
                "description": "PubMed Question Answering",
                "use_case": "Scientific document RAG",
                "size": "~200K",
                "recommended_limit": 1000,
            },
            {
                "name": "google-research-datasets/natural_questions",
                "description": "Natural Questions from Google",
                "use_case": "General QA",
                "size": "~300K",
                "recommended_limit": 500,
            },
            {
                "name": "multidoc2dial",
                "description": "Multi-Document Dialogue",
                "use_case": "Multi-doc dialogue",
                "size": "Varies",
                "recommended_limit": 500,
            },
            {
                "name": "wikitext",
                "description": "Wikipedia Text",
                "use_case": "General knowledge RAG",
                "size": "~100M tokens",
                "recommended_limit": 1000,
            },
        ],
        "tips": [
            "Start with small limits (100-500) for testing",
            "Use 'rajpurkar/squad' for document QA testing",
            "Set HUGGINGFACE_TOKEN in .env for gated datasets",
            "All datasets are chunked using your 512-token chunker",
            "Duplicates are automatically handled via content_hash",
        ],
    }
