"""Compatibility shim for job model imports.

Re-exports JobStatus and JobType from processing_job module
to maintain backward compatibility with code that imports from
src.storage_indexing.models.job.
"""

from src.storage_indexing.models.processing_job import JobStatus, JobType

__all__ = ["JobStatus", "JobType"]
