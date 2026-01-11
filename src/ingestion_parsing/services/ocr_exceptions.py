"""Custom exceptions for OCR operations.

Feature: 004-ocr-embedding-pipeline
Task: T029
"""


class OcrError(Exception):
    """Base exception for OCR-related errors."""

    pass


class OcrEngineNotAvailableError(OcrError):
    """Raised when the requested OCR engine is not available."""

    def __init__(self, engine: str) -> None:
        """Initialize exception with engine name.

        Args:
            engine: OCR engine that is not available
        """
        self.engine = engine
        super().__init__(f"OCR engine not available: {engine}")


class OcrProcessingError(OcrError):
    """Raised when OCR processing fails for a document."""

    def __init__(self, document_id: int, reason: str) -> None:
        """Initialize exception with document ID and reason.

        Args:
            document_id: Document ID that failed processing
            reason: Reason for failure
        """
        self.document_id = document_id
        self.reason = reason
        super().__init__(
            f"OCR processing failed for document {document_id}: {reason}"
        )


class OcrConfidenceTooLowError(OcrError):
    """Raised when OCR confidence is below acceptable threshold."""

    def __init__(self, confidence: float, threshold: float) -> None:
        """Initialize exception with confidence and threshold.

        Args:
            confidence: Actual confidence score
            threshold: Minimum acceptable threshold
        """
        self.confidence = confidence
        self.threshold = threshold
        super().__init__(
            f"OCR confidence {confidence:.2f} below threshold {threshold:.2f}"
        )


class UnsupportedLanguageError(OcrError):
    """Raised when language is not supported by OCR engine."""

    def __init__(self, language: str, engine: str) -> None:
        """Initialize exception with language and engine.

        Args:
            language: Language code that is not supported
            engine: OCR engine name
        """
        self.language = language
        self.engine = engine
        super().__init__(
            f"Language '{language}' not supported by OCR engine: {engine}"
        )


class DocumentNotFoundError(OcrError):
    """Raised when document is not found."""

    def __init__(self, document_id: int) -> None:
        """Initialize exception with document ID.

        Args:
            document_id: Document ID that was not found
        """
        self.document_id = document_id
        super().__init__(f"Document not found: {document_id}")


class DocumentAlreadyProcessedError(OcrError):
    """Raised when attempting to process an already processed document."""

    def __init__(self, document_id: int) -> None:
        """Initialize exception with document ID.

        Args:
            document_id: Document ID that is already processed
        """
        self.document_id = document_id
        super().__init__(
            f"Document {document_id} already processed. Use force_reprocess=True to reprocess."
        )
