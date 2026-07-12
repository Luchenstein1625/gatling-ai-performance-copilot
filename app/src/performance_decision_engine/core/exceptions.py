class PDEError(Exception):
    """Base exception for the application."""


class InputFileError(PDEError):
    """Raised when an input file is missing or invalid."""
