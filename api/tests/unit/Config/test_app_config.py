"""
Unit tests for AppConfig class.
"""

import os
import sys
import tempfile
import pytest
import re
from unittest.mock import patch, Mock
from pydantic import ValidationError

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
sys.path.insert(0, project_root)

from src.Config.AppConfig import AppConfig, OSType

class TestOSType:
    """Test cases for OSType enum."""
    
    def test_os_type_values(self):
        """Test OSType enum values."""
        assert OSType.WINDOWS == "nt"
        assert OSType.LINUX == "posix"
        assert OSType.MACOS == "darwin"
        assert OSType.OTHER == "other"


class TestAppConfig:
    """Test cases for AppConfig class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def valid_config_data(self, temp_dir):
        """Provide valid configuration data for testing."""
        return {
            "app_name": "TestApp",
            "version": "1.0.0",
            "debug": False,
            "database_url": "postgresql://localhost:5432/test",
            "port": 8080,
            "host": "0.0.0.0",
            "filesystem_path": temp_dir,
            "encryption_secret": "test_secret_key",
            "log_target": "console"
        }
    
    def test_init_with_valid_data(self, valid_config_data):
        """Test AppConfig initialization with valid data."""
        config = AppConfig(**valid_config_data)
        
        assert config.app_name == "TestApp"
        assert config.version == "1.0.0"
        assert config.debug is False
        assert config.database_url == "postgresql://localhost:5432/test"
        assert config.port == 8080
        assert config.host == "0.0.0.0"
        assert config.filesystem_path == valid_config_data["filesystem_path"]
        assert config.encryption_secret == "test_secret_key"
        assert config.log_target == "console"
    
    def test_operating_system_default(self, valid_config_data):
        """Test operating system is set correctly and is a valid OSType."""
        config = AppConfig(**valid_config_data)
        assert isinstance(config.operating_system, OSType)
        assert config.operating_system in [OSType.WINDOWS, OSType.LINUX, OSType.MACOS, OSType.OTHER]
    
    def test_default_values(self, temp_dir):
        """Test default values are applied correctly."""
        config = AppConfig(
            app_name="TestApp",
            version="1.0.0",
            database_url="sqlite:///:memory:",
            filesystem_path=temp_dir,
            encryption_secret="secret",
            log_target="console"
        ) # type: ignore
        
        assert config.debug is False
        assert config.database_url == "sqlite:///:memory:"
        assert config.port == 8000
        assert config.host == "localhost"


class TestAppConfigFromEnv:
    """Test cases for AppConfig.from_env() method."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_from_env_with_all_env_vars(self, temp_dir):
        """Test from_env with all environment variables set."""
        env_vars = {
            "APP_NAME": "EnvApp",
            "VERSION": "2.1.3",
            "DEBUG": "true",
            "DATABASE_URL": "postgresql://env:5432/envdb",
            "PORT": "9000",
            "HOST": "env.example.com",
            "FILESYSTEM_PATH": temp_dir,
            "ENCRYPTION_SECRET": "env_secret",
            "LOG_TARGET": "file"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = AppConfig.from_env()
            
            assert config.app_name == "EnvApp"
            assert config.version == "2.1.3"
            assert config.debug is True
            assert config.database_url == "postgresql://env:5432/envdb"
            assert config.port == 9000
            assert config.host == "env.example.com"
            assert config.filesystem_path == temp_dir
            assert config.encryption_secret == "env_secret"
            assert config.log_target == "file"
    
    def test_from_env_with_defaults(self, temp_dir):
        """Test from_env with default values when env vars are not set."""
        # Create default filesystem path
        default_path = "/tmp/MiraVeja"
        os.makedirs(default_path, exist_ok=True)

        with patch.dict(os.environ, {"FILESYSTEM_PATH": temp_dir, "DATABASE_URL": "sqlite:///:memory:"}, clear=True):
            config = AppConfig.from_env()
            
            assert config.app_name == "MiraVeja"
            assert config.version == "1.0.0"
            assert config.debug is False
            assert config.database_url == "sqlite:///:memory:"
            assert config.port == 8000
            assert config.host == "localhost"
            assert config.filesystem_path == temp_dir
            assert config.encryption_secret == "my_secret_key"
            assert config.log_target == "console"
    
    def test_from_env_debug_case_insensitive(self, temp_dir):
        """Test DEBUG environment variable is case insensitive."""
        test_cases = ["true", "True", "TRUE", "false", "False", "FALSE", "invalid"]
        expected = [True, True, True, False, False, False, False]
        
        for debug_value, expected_result in zip(test_cases, expected):
            env_vars = {"DEBUG": debug_value, "FILESYSTEM_PATH": temp_dir, "DATABASE_URL": "sqlite:///:memory:"}
            with patch.dict(os.environ, env_vars, clear=True):
                config = AppConfig.from_env()
                assert config.debug == expected_result


class TestAppConfigValidators:
    """Test cases for AppConfig field validators."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def base_config_data(self, temp_dir):
        """Provide base configuration data for validator testing."""
        return {
            "app_name": "TestApp",
            "database_url": "sqlite:///:memory:",
            "version": "1.0.0",
            "filesystem_path": temp_dir,
            "encryption_secret": "secret",
            "log_target": "console"
        }


class TestFilesystemPathValidator:
    """Test cases for filesystem_path validator."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    @pytest.fixture
    def base_config_data(self):
        """Provide base configuration data."""
        return {
            "app_name": "TestApp",
            "database_url": "sqlite:///:memory:",
            "version": "1.0.0",
            "encryption_secret": "secret",
            "log_target": "console"
        }
    
    def test_valid_filesystem_path(self, base_config_data, temp_dir):
        """Test valid filesystem path."""
        base_config_data["filesystem_path"] = temp_dir
        config = AppConfig(**base_config_data)
        assert config.filesystem_path == temp_dir
    
    def test_relative_path_raises_error(self, base_config_data):
        """Test relative path raises ValueError."""
        base_config_data["filesystem_path"] = "relative/path"
        with pytest.raises(ValidationError) as exc_info:
            AppConfig(**base_config_data)
        assert "Filesystem path must be an absolute path" in str(exc_info.value)
    
    def test_nonexistent_path_raises_error(self, base_config_data):
        """Test nonexistent path raises ValueError."""
        base_config_data["filesystem_path"] = "/nonexistent/path"
        with pytest.raises(ValidationError) as exc_info:
            AppConfig(**base_config_data)
        assert "does not exist" in str(exc_info.value)
    
    def test_non_writable_path_raises_error(self, base_config_data, temp_dir):
        """Test non-writable path raises ValueError."""
        # Make directory read-only
        os.chmod(temp_dir, 0o444)
        base_config_data["filesystem_path"] = temp_dir
        
        try:
            with pytest.raises(ValidationError) as exc_info:
                AppConfig(**base_config_data)
            assert "is not writable" in str(exc_info.value)
        finally:
            # Restore write permissions for cleanup
            os.chmod(temp_dir, 0o755)
    
    @patch('os.name', 'posix')
    def test_unix_path_validation(self, base_config_data, temp_dir):
        """Test Unix path validation with valid characters."""
        valid_paths = [temp_dir]
        
        for path in valid_paths:
            base_config_data["filesystem_path"] = path
            config = AppConfig(**base_config_data)
            assert config.filesystem_path == path
    
    @patch('os.name', 'nt')
    def test_windows_path_validation(self, base_config_data):
        """Test Windows path validation."""
        # Mock a Windows path that exists and is writable
        windows_path = "C:\\temp\\test"
        
        with patch('os.path.isabs', return_value=True), \
             patch('os.path.exists', return_value=True), \
             patch('os.access', return_value=True):
            
            base_config_data["filesystem_path"] = windows_path
            config = AppConfig(**base_config_data)
            assert config.filesystem_path == windows_path
    
    def test_invalid_characters_in_path(self, base_config_data, temp_dir):
        """Test path with invalid characters raises ValueError."""
        # Create a path with invalid characters for Unix systems
        with patch('os.name', 'posix'):
            invalid_path = temp_dir.replace(temp_dir.split('/')[-1], 'invalid|path')
            
            with patch('os.path.exists', return_value=True), \
                 patch('os.access', return_value=True):
                
                base_config_data["filesystem_path"] = invalid_path
                with pytest.raises(ValidationError) as exc_info:
                    AppConfig(**base_config_data)
                assert "contains invalid characters" in str(exc_info.value)


class TestPortValidator:
    """Test cases for port validator."""
    
    @pytest.fixture
    def base_config_data(self, temp_dir):
        """Provide base configuration data."""
        return {
            "app_name": "TestApp",
            "database_url": "sqlite:///:memory:",
            "version": "1.0.0",
            "filesystem_path": temp_dir,
            "encryption_secret": "secret",
            "log_target": "console"
        }
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_valid_ports(self, base_config_data):
        """Test valid port numbers."""
        valid_ports = [1, 80, 443, 8000, 8080, 65535]
        
        for port in valid_ports:
            base_config_data["port"] = port
            config = AppConfig(**base_config_data)
            assert config.port == port
    
    def test_invalid_ports(self, base_config_data):
        """Test invalid port numbers raise ValueError."""
        invalid_ports = [0, -1, 65536, 100000]
        
        for port in invalid_ports:
            base_config_data["port"] = port
            with pytest.raises(ValidationError) as exc_info:
                AppConfig(**base_config_data)
            assert "Port must be between 1 and 65535" in str(exc_info.value)


class TestDebugValidator:
    """Test cases for debug validator."""
    
    @pytest.fixture
    def base_config_data(self, temp_dir):
        """Provide base configuration data."""
        return {
            "app_name": "TestApp",
            "database_url": "sqlite:///:memory:",
            "version": "1.0.0",
            "filesystem_path": temp_dir,
            "encryption_secret": "secret",
            "log_target": "console"
        }
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_valid_debug_values(self, base_config_data):
        """Test valid debug boolean values."""
        valid_values = [True, False]
        
        for value in valid_values:
            base_config_data["debug"] = value
            config = AppConfig(**base_config_data)
            assert config.debug == value


class TestHostValidator:
    """Test cases for host validator."""
    
    @pytest.fixture
    def base_config_data(self, temp_dir):
        """Provide base configuration data."""
        return {
            "app_name": "TestApp",
            "database_url": "sqlite:///:memory:",
            "version": "1.0.0",
            "filesystem_path": temp_dir,
            "encryption_secret": "secret",
            "log_target": "console"
        }
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_valid_hosts(self, base_config_data):
        """Test valid host values."""
        valid_hosts = ["localhost", "0.0.0.0", "example.com", "192.168.1.1"]
        
        for host in valid_hosts:
            base_config_data["host"] = host
            config = AppConfig(**base_config_data)
            assert config.host == host
    
    def test_empty_host_raises_error(self, base_config_data):
        """Test empty host raises ValueError."""
        base_config_data["host"] = ""
        with pytest.raises(ValidationError) as exc_info:
            AppConfig(**base_config_data)
        assert "Host cannot be empty" in str(exc_info.value)


class TestAppNameValidator:
    """Test cases for app_name validator."""
    
    @pytest.fixture
    def base_config_data(self, temp_dir):
        """Provide base configuration data."""
        return {
            "version": "1.0.0",
            "database_url": "sqlite:///:memory:",
            "filesystem_path": temp_dir,
            "encryption_secret": "secret",
            "log_target": "console"
        }
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_valid_app_names(self, base_config_data):
        """Test valid application names."""
        valid_names = ["TestApp", "MyApp123", "app_name", "APP_NAME_123"]
        
        for name in valid_names:
            base_config_data["app_name"] = name
            config = AppConfig(**base_config_data)
            assert config.app_name == name
    
    def test_empty_app_name_raises_error(self, base_config_data):
        """Test empty app name raises ValueError."""
        base_config_data["app_name"] = ""
        with pytest.raises(ValidationError) as exc_info:
            AppConfig(**base_config_data)
        assert "Application name cannot be empty" in str(exc_info.value)
    
    def test_invalid_app_name_characters_raise_error(self, base_config_data):
        """Test app names with invalid characters raise ValueError."""
        invalid_names = ["App-Name", "App Name", "App@Name", "App.Name", "App/Name"]
        
        for name in invalid_names:
            base_config_data["app_name"] = name
            with pytest.raises(ValidationError) as exc_info:
                AppConfig(**base_config_data)
            assert "must contain only alphanumeric characters and underscores" in str(exc_info.value)


class TestVersionValidator:
    """Test cases for version validator."""
    
    @pytest.fixture
    def base_config_data(self, temp_dir):
        """Provide base configuration data."""
        return {
            "app_name": "TestApp",
            "filesystem_path": temp_dir,
            "database_url": "sqlite:///:memory:",
            "encryption_secret": "secret",
            "log_target": "console"
        }
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_valid_versions(self, base_config_data):
        """Test valid version formats."""
        valid_versions = ["1.0.0", "0.1.0", "10.20.30", "999.999.999"]
        
        for version in valid_versions:
            base_config_data["version"] = version
            config = AppConfig(**base_config_data)
            assert config.version == version
    
    def test_empty_version_raises_error(self, base_config_data):
        """Test empty version raises ValueError."""
        base_config_data["version"] = ""
        with pytest.raises(ValidationError) as exc_info:
            AppConfig(**base_config_data)
        assert "Version cannot be empty" in str(exc_info.value)
    
    def test_invalid_version_formats_raise_error(self, base_config_data):
        """Test invalid version formats raise ValueError."""
        invalid_versions = ["1.0", "1.0.0.0", "v1.0.0", "1.0.0-beta", "1.x.0", "1.0.0a"]
        
        for version in invalid_versions:
            base_config_data["version"] = version
            with pytest.raises(ValidationError) as exc_info:
                AppConfig(**base_config_data)
            assert "Version must be in the format X.Y.Z" in str(exc_info.value)


class TestAppConfigIntegration:
    """Integration tests for AppConfig class."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield temp_dir
    
    def test_complete_config_creation_and_validation(self, temp_dir):
        """Test complete configuration creation with all validations."""
        config_data = {
            "app_name": "MiraVeja",
            "version": "1.2.3",
            "debug": True,
            "database_url": "postgresql://localhost:5432/miraveja",
            "port": 8080,
            "host": "0.0.0.0",
            "filesystem_path": temp_dir,
            "encryption_secret": "super_secret_key_123",
            "log_target": "file"
        }
        
        config = AppConfig(**config_data)
        
        # Verify all fields are set correctly
        assert config.app_name == "MiraVeja"
        assert config.version == "1.2.3"
        assert config.debug is True
        assert config.database_url == "postgresql://localhost:5432/miraveja"
        assert config.port == 8080
        assert config.host == "0.0.0.0"
        assert config.filesystem_path == temp_dir
        assert config.encryption_secret == "super_secret_key_123"
        assert config.log_target == "file"
        assert isinstance(config.operating_system, OSType)
    
    def test_from_env_integration(self, temp_dir):
        """Test from_env method integration with environment variables."""
        env_vars = {
            "APP_NAME": "MiraVeja_Test",
            "VERSION": "2.0.1",
            "DEBUG": "true",
            "DATABASE_URL": "postgresql://test:5432/test_db",
            "PORT": "9090",
            "HOST": "test.localhost",
            "FILESYSTEM_PATH": temp_dir,
            "ENCRYPTION_SECRET": "test_secret_123",
            "LOG_TARGET": "both"
        }
        
        with patch.dict(os.environ, env_vars, clear=True):
            config = AppConfig.from_env()
            
            assert config.app_name == "MiraVeja_Test"
            assert config.version == "2.0.1"
            assert config.debug is True
            assert config.database_url == "postgresql://test:5432/test_db"
            assert config.port == 9090
            assert config.host == "test.localhost"
            assert config.filesystem_path == temp_dir
            assert config.encryption_secret == "test_secret_123"
            assert config.log_target == "both"
