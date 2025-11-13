from MiravejaCore.Shared.Errors.Models import DomainException


class VectorNotFoundException(DomainException):
    """Exception raised when a vector is not found."""

    def __init__(self, vectorId: str) -> None:
        super().__init__(f"Vector with ID '{vectorId}' not found.")


class VectorGenerationFailedException(DomainException):
    """Exception raised when vector generation fails."""

    def __init__(self, reason: str) -> None:
        super().__init__(f"Vector generation failed: {reason}.")


class InvalidVectorTypeException(DomainException):
    """Exception raised when an invalid vector type is provided."""

    def __init__(self, vectorType: str) -> None:
        super().__init__(f"Invalid vector type: '{vectorType}'.")


class InvalidEmbeddingDimensionException(DomainException):
    """Exception raised when the embedding dimension is invalid."""

    def __init__(self, expectedDim: int, actualDim: int) -> None:
        super().__init__(f"Invalid embedding dimension: expected {expectedDim}, got {actualDim}.")


class VectorsAndWeightsMismatchException(DomainException):
    """Exception raised when the number of vectors and weights do not match."""

    def __init__(self, numVectors: int, numWeights: int) -> None:
        super().__init__(f"Number of vectors ({numVectors}) does not match number of weights ({numWeights}).")


class VectorsDimensionMismatchException(DomainException):
    """Exception raised when vectors have mismatched dimensions."""

    def __init__(self, dimA: int, dimB: int) -> None:
        super().__init__(f"Vector dimension mismatch: {dimA} vs {dimB}.")


class EmbeddingMustBeOneDimensionalException(DomainException):
    """Exception raised when the embedding is not one-dimensional."""

    def __init__(self, actualDim: int) -> None:
        super().__init__(f"Embedding must be one-dimensional, got {actualDim} dimensions.")


class EmbeddingMustBeNormalizedException(DomainException):
    """Exception raised when the embedding is not normalized."""

    def __init__(self, normValue: float) -> None:
        super().__init__(f"Embedding must be normalized (norm=1), got norm={normValue}.")


class EmbeddingOnCUDANotSupportedException(DomainException):
    """Exception raised when the embedding is on CUDA device."""

    def __init__(self) -> None:
        super().__init__("Embedding is on CUDA device, operation requires CPU tensor.")
