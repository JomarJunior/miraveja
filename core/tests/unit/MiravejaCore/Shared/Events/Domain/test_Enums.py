import pytest

from MiravejaCore.Shared.Events.Domain.Enums import (
    ProducerAcksLevel,
    ConsumerAutoOffsetReset,
    SecurityProtocol,
    SaslMechanism,
    CompressionType,
)


class TestProducerAcksLevel:
    """Test cases for ProducerAcksLevel enumeration."""

    def test_AllAcksLevel_ShouldHaveCorrectValue(self):
        """Test that ALL acknowledgment level has correct value."""
        # Act & Assert
        assert ProducerAcksLevel.ALL == "all"
        assert ProducerAcksLevel.ALL.value == "all"
        assert str(ProducerAcksLevel.ALL) == "all"

    def test_LeaderAcksLevel_ShouldHaveCorrectValue(self):
        """Test that LEADER acknowledgment level has correct value."""
        # Act & Assert
        assert ProducerAcksLevel.LEADER == "1"
        assert ProducerAcksLevel.LEADER.value == "1"
        assert str(ProducerAcksLevel.LEADER) == "1"

    def test_NoneAcksLevel_ShouldHaveCorrectValue(self):
        """Test that NONE acknowledgment level has correct value."""
        # Act & Assert
        assert ProducerAcksLevel.NONE == "0"
        assert ProducerAcksLevel.NONE.value == "0"
        assert str(ProducerAcksLevel.NONE) == "0"

    def test_AllEnumValues_ShouldBeStringType(self):
        """Test that all ProducerAcksLevel values are strings."""
        # Act & Assert
        for level in ProducerAcksLevel:
            assert isinstance(level.value, str)
            assert isinstance(str(level), str)


class TestConsumerAutoOffsetReset:
    """Test cases for ConsumerAutoOffsetReset enumeration."""

    def test_EarliestOffsetReset_ShouldHaveCorrectValue(self):
        """Test that EARLIEST offset reset has correct value."""
        # Act & Assert
        assert ConsumerAutoOffsetReset.EARLIEST == "earliest"
        assert ConsumerAutoOffsetReset.EARLIEST.value == "earliest"
        assert str(ConsumerAutoOffsetReset.EARLIEST) == "earliest"

    def test_LatestOffsetReset_ShouldHaveCorrectValue(self):
        """Test that LATEST offset reset has correct value."""
        # Act & Assert
        assert ConsumerAutoOffsetReset.LATEST == "latest"
        assert ConsumerAutoOffsetReset.LATEST.value == "latest"
        assert str(ConsumerAutoOffsetReset.LATEST) == "latest"

    def test_NoneOffsetReset_ShouldHaveCorrectValue(self):
        """Test that NONE offset reset has correct value."""
        # Act & Assert
        assert ConsumerAutoOffsetReset.NONE == "none"
        assert ConsumerAutoOffsetReset.NONE.value == "none"
        assert str(ConsumerAutoOffsetReset.NONE) == "none"

    def test_AllEnumValues_ShouldBeStringType(self):
        """Test that all ConsumerAutoOffsetReset values are strings."""
        # Act & Assert
        for reset in ConsumerAutoOffsetReset:
            assert isinstance(reset.value, str)
            assert isinstance(str(reset), str)


class TestSecurityProtocol:
    """Test cases for SecurityProtocol enumeration."""

    def test_PlaintextProtocol_ShouldHaveCorrectValue(self):
        """Test that PLAINTEXT protocol has correct value."""
        # Act & Assert
        assert SecurityProtocol.PLAINTEXT == "PLAINTEXT"
        assert SecurityProtocol.PLAINTEXT.value == "PLAINTEXT"
        assert str(SecurityProtocol.PLAINTEXT) == "PLAINTEXT"

    def test_SslProtocol_ShouldHaveCorrectValue(self):
        """Test that SSL protocol has correct value."""
        # Act & Assert
        assert SecurityProtocol.SSL == "SSL"
        assert SecurityProtocol.SSL.value == "SSL"
        assert str(SecurityProtocol.SSL) == "SSL"

    def test_SaslPlaintextProtocol_ShouldHaveCorrectValue(self):
        """Test that SASL_PLAINTEXT protocol has correct value."""
        # Act & Assert
        assert SecurityProtocol.SASL_PLAINTEXT == "SASL_PLAINTEXT"
        assert SecurityProtocol.SASL_PLAINTEXT.value == "SASL_PLAINTEXT"
        assert str(SecurityProtocol.SASL_PLAINTEXT) == "SASL_PLAINTEXT"

    def test_SaslSslProtocol_ShouldHaveCorrectValue(self):
        """Test that SASL_SSL protocol has correct value."""
        # Act & Assert
        assert SecurityProtocol.SASL_SSL == "SASL_SSL"
        assert SecurityProtocol.SASL_SSL.value == "SASL_SSL"
        assert str(SecurityProtocol.SASL_SSL) == "SASL_SSL"

    def test_AllEnumValues_ShouldBeStringType(self):
        """Test that all SecurityProtocol values are strings."""
        # Act & Assert
        for protocol in SecurityProtocol:
            assert isinstance(protocol.value, str)
            assert isinstance(str(protocol), str)

    def test_AllEnumValues_ShouldBeUppercase(self):
        """Test that all SecurityProtocol values are uppercase."""
        # Act & Assert
        for protocol in SecurityProtocol:
            assert protocol.value.isupper()


class TestSaslMechanism:
    """Test cases for SaslMechanism enumeration."""

    def test_PlainMechanism_ShouldHaveCorrectValue(self):
        """Test that PLAIN mechanism has correct value."""
        # Act & Assert
        assert SaslMechanism.PLAIN == "PLAIN"
        assert SaslMechanism.PLAIN.value == "PLAIN"
        assert str(SaslMechanism.PLAIN) == "PLAIN"

    def test_ScramSha256Mechanism_ShouldHaveCorrectValue(self):
        """Test that SCRAM_SHA_256 mechanism has correct value."""
        # Act & Assert
        assert SaslMechanism.SCRAM_SHA_256 == "SCRAM-SHA-256"
        assert SaslMechanism.SCRAM_SHA_256.value == "SCRAM-SHA-256"
        assert str(SaslMechanism.SCRAM_SHA_256) == "SCRAM-SHA-256"

    def test_ScramSha512Mechanism_ShouldHaveCorrectValue(self):
        """Test that SCRAM_SHA_512 mechanism has correct value."""
        # Act & Assert
        assert SaslMechanism.SCRAM_SHA_512 == "SCRAM-SHA-512"
        assert SaslMechanism.SCRAM_SHA_512.value == "SCRAM-SHA-512"
        assert str(SaslMechanism.SCRAM_SHA_512) == "SCRAM-SHA-512"

    def test_AllEnumValues_ShouldBeStringType(self):
        """Test that all SaslMechanism values are strings."""
        # Act & Assert
        for mechanism in SaslMechanism:
            assert isinstance(mechanism.value, str)
            assert isinstance(str(mechanism), str)

    def test_ScramMechanisms_ShouldContainHyphen(self):
        """Test that SCRAM mechanisms contain hyphen character."""
        # Act & Assert
        assert "-" in SaslMechanism.SCRAM_SHA_256.value
        assert "-" in SaslMechanism.SCRAM_SHA_512.value
        assert "-" not in SaslMechanism.PLAIN.value


class TestCompressionType:
    """Test cases for CompressionType enumeration."""

    def test_NoneCompression_ShouldHaveCorrectValue(self):
        """Test that NONE compression has correct value."""
        # Act & Assert
        assert CompressionType.NONE == "none"
        assert CompressionType.NONE.value == "none"
        assert str(CompressionType.NONE) == "none"

    def test_GzipCompression_ShouldHaveCorrectValue(self):
        """Test that GZIP compression has correct value."""
        # Act & Assert
        assert CompressionType.GZIP == "gzip"
        assert CompressionType.GZIP.value == "gzip"
        assert str(CompressionType.GZIP) == "gzip"

    def test_SnappyCompression_ShouldHaveCorrectValue(self):
        """Test that SNAPPY compression has correct value."""
        # Act & Assert
        assert CompressionType.SNAPPY == "snappy"
        assert CompressionType.SNAPPY.value == "snappy"
        assert str(CompressionType.SNAPPY) == "snappy"

    def test_Lz4Compression_ShouldHaveCorrectValue(self):
        """Test that LZ4 compression has correct value."""
        # Act & Assert
        assert CompressionType.LZ4 == "lz4"
        assert CompressionType.LZ4.value == "lz4"
        assert str(CompressionType.LZ4) == "lz4"

    def test_ZstdCompression_ShouldHaveCorrectValue(self):
        """Test that ZSTD compression has correct value."""
        # Act & Assert
        assert CompressionType.ZSTD == "zstd"
        assert CompressionType.ZSTD.value == "zstd"
        assert str(CompressionType.ZSTD) == "zstd"

    def test_AllEnumValues_ShouldBeStringType(self):
        """Test that all CompressionType values are strings."""
        # Act & Assert
        for compression in CompressionType:
            assert isinstance(compression.value, str)
            assert isinstance(str(compression), str)

    def test_AllEnumValues_ShouldBeLowercase(self):
        """Test that all CompressionType values are lowercase."""
        # Act & Assert
        for compression in CompressionType:
            assert compression.value.islower()

    def test_CompressionTypeCount_ShouldHaveFiveOptions(self):
        """Test that CompressionType has exactly five compression options."""
        # Act
        compressionTypes = list(CompressionType)

        # Assert
        assert len(compressionTypes) == 5
        expectedTypes = {"none", "gzip", "snappy", "lz4", "zstd"}
        actualTypes = {compression.value for compression in compressionTypes}
        assert actualTypes == expectedTypes


class TestEnumInteroperability:
    """Test cases for enum interoperability and usage patterns."""

    def test_EnumEquality_ShouldWorkWithStringValues(self):
        """Test that enums can be compared with their string values."""
        # Act & Assert
        assert ProducerAcksLevel.ALL == "all"
        assert SecurityProtocol.SSL == "SSL"
        assert CompressionType.GZIP == "gzip"

    def test_EnumInCollections_ShouldWorkCorrectly(self):
        """Test that enums work correctly in collections."""
        # Arrange
        protocols = [SecurityProtocol.PLAINTEXT, SecurityProtocol.SSL]
        compressions = {CompressionType.GZIP, CompressionType.SNAPPY}

        # Act & Assert
        assert SecurityProtocol.PLAINTEXT in protocols
        assert SecurityProtocol.SASL_SSL not in protocols
        assert CompressionType.GZIP in compressions
        assert CompressionType.LZ4 not in compressions

    def test_EnumStringConversion_ShouldBeConsistent(self):
        """Test that enum string conversion is consistent across all enums."""
        # Act & Assert
        assert str(ProducerAcksLevel.ALL) == ProducerAcksLevel.ALL.value
        assert str(ConsumerAutoOffsetReset.EARLIEST) == ConsumerAutoOffsetReset.EARLIEST.value
        assert str(SecurityProtocol.SSL) == SecurityProtocol.SSL.value
        assert str(SaslMechanism.PLAIN) == SaslMechanism.PLAIN.value
        assert str(CompressionType.GZIP) == CompressionType.GZIP.value

    def test_EnumIterability_ShouldWorkForAllEnums(self):
        """Test that all enums are iterable."""
        # Act & Assert
        assert len(list(ProducerAcksLevel)) == 3
        assert len(list(ConsumerAutoOffsetReset)) == 3
        assert len(list(SecurityProtocol)) == 4
        assert len(list(SaslMechanism)) == 3
        assert len(list(CompressionType)) == 5
