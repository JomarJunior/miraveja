import pytest

from MiravejaCore.Shared.Logging.Enums import LoggerLevel, LoggerTarget


class TestLoggerLevel:
    """Test cases for LoggerLevel enum."""

    def test_DebugValue_ShouldReturnDebugString(self):
        """Test that DEBUG enum has correct value."""
        assert LoggerLevel.DEBUG.value == "DEBUG"

    def test_InfoValue_ShouldReturnInfoString(self):
        """Test that INFO enum has correct value."""
        assert LoggerLevel.INFO.value == "INFO"

    def test_WarningValue_ShouldReturnWarningString(self):
        """Test that WARNING enum has correct value."""
        assert LoggerLevel.WARNING.value == "WARNING"

    def test_ErrorValue_ShouldReturnErrorString(self):
        """Test that ERROR enum has correct value."""
        assert LoggerLevel.ERROR.value == "ERROR"

    def test_CriticalValue_ShouldReturnCriticalString(self):
        """Test that CRITICAL enum has correct value."""
        assert LoggerLevel.CRITICAL.value == "CRITICAL"

    def test_StrMethod_ShouldReturnEnumValue(self):
        """Test that __str__ method returns the enum value."""
        assert str(LoggerLevel.DEBUG) == "DEBUG"
        assert str(LoggerLevel.INFO) == "INFO"
        assert str(LoggerLevel.WARNING) == "WARNING"
        assert str(LoggerLevel.ERROR) == "ERROR"
        assert str(LoggerLevel.CRITICAL) == "CRITICAL"


class TestLoggerTarget:
    """Test cases for LoggerTarget enum."""

    def test_ConsoleValue_ShouldReturnConsoleString(self):
        """Test that CONSOLE enum has correct value."""
        assert LoggerTarget.CONSOLE.value == "CONSOLE"

    def test_FileValue_ShouldReturnFileString(self):
        """Test that FILE enum has correct value."""
        assert LoggerTarget.FILE.value == "FILE"

    def test_JsonValue_ShouldReturnJsonString(self):
        """Test that JSON enum has correct value."""
        assert LoggerTarget.JSON.value == "JSON"

    def test_StrMethod_ShouldReturnEnumValue(self):
        """Test that __str__ method returns the enum value."""
        assert str(LoggerTarget.CONSOLE) == "CONSOLE"
        assert str(LoggerTarget.FILE) == "FILE"
        assert str(LoggerTarget.JSON) == "JSON"
