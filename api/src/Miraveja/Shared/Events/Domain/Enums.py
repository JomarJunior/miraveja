from enum import Enum


class ProducerAcksLevel(str, Enum):
    """Enumeration for Kafka producer acknowledgment levels."""

    ALL = "all"
    LEADER = "1"
    NONE = "0"

    def __str__(self) -> str:
        return self.value


class ConsumerAutoOffsetReset(str, Enum):
    """Enumeration for Kafka consumer auto offset reset policies."""

    EARLIEST = "earliest"
    LATEST = "latest"
    NONE = "none"

    def __str__(self) -> str:
        return self.value


class SecurityProtocol(str, Enum):
    """Enumeration for Kafka security protocols."""

    PLAINTEXT = "PLAINTEXT"
    SSL = "SSL"
    SASL_PLAINTEXT = "SASL_PLAINTEXT"
    SASL_SSL = "SASL_SSL"

    def __str__(self) -> str:
        return self.value


class SaslMechanism(str, Enum):
    """Enumeration for SASL mechanisms."""

    PLAIN = "PLAIN"
    SCRAM_SHA_256 = "SCRAM-SHA-256"
    SCRAM_SHA_512 = "SCRAM-SHA-512"

    def __str__(self) -> str:
        return self.value


class CompressionType(str, Enum):
    """Enumeration for Kafka compression types."""

    NONE = "none"
    GZIP = "gzip"
    SNAPPY = "snappy"
    LZ4 = "lz4"
    ZSTD = "zstd"

    def __str__(self) -> str:
        return self.value
