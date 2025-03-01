"""
Configuration Loader module for managing framework settings.

This module provides functionality to load and validate configuration settings
from YAML files and environment variables.
"""

from typing import Dict, Any, Optional
import os
from pathlib import Path
import yaml
from dataclasses import dataclass
from dotenv import load_dotenv

@dataclass
class BrowserConfig:
    """Browser configuration settings."""
    name: str
    headless: bool
    window_size: tuple[int, int]
    implicit_wait: int
    page_load_timeout: int

@dataclass
class TestConfig:
    """Test execution configuration settings."""
    base_url: str
    screenshot_dir: str
    report_dir: str
    log_dir: str
    retry_attempts: int
    wait_timeout: int

@dataclass
class FrameworkConfig:
    """Complete framework configuration."""
    browser: BrowserConfig
    test: TestConfig
    custom_settings: Dict[str, Any]

class ConfigurationError(Exception):
    """Custom exception for configuration errors."""
    pass

class ConfigLoader:
    """Main class for loading and managing framework configuration."""

    # Default configuration values
    DEFAULT_CONFIG = {
        'browser': {
            'name': 'chrome',
            'headless': False,
            'window_size': (1920, 1080),
            'implicit_wait': 10,
            'page_load_timeout': 30
        },
        'test': {
            'base_url': 'http://localhost',
            'screenshot_dir': 'test_output/screenshots',
            'report_dir': 'test_output/reports',
            'log_dir': 'test_output/logs',
            'retry_attempts': 2,
            'wait_timeout': 10
        }
    }

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the configuration loader.

        Args:
            config_path: Optional path to configuration file
        """
        self.config_path = config_path
        load_dotenv()  # Load environment variables from .env file
        self.config = self._load_configuration()

    def _load_configuration(self) -> FrameworkConfig:
        """
        Load and validate configuration from file and environment variables.

        Returns:
            FrameworkConfig: Complete framework configuration

        Raises:
            ConfigurationError: If configuration is invalid
        """
        # Start with default configuration
        config = self.DEFAULT_CONFIG.copy()

        # Load configuration from file if provided
        if self.config_path:
            file_config = self._load_config_file()
            config = self._merge_configs(config, file_config)

        # Override with environment variables
        config = self._apply_environment_variables(config)

        # Validate and create configuration objects
        return self._create_config_objects(config)

    def _load_config_file(self) -> Dict:
        """
        Load configuration from YAML file.

        Returns:
            Dict: Configuration from file

        Raises:
            ConfigurationError: If file cannot be loaded
        """
        try:
            with open(self.config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            raise ConfigurationError(f"Failed to load configuration file: {str(e)}")

    def _merge_configs(self, base: Dict, override: Dict) -> Dict:
        """
        Merge two configuration dictionaries.

        Args:
            base: Base configuration
            override: Override configuration

        Returns:
            Dict: Merged configuration
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._merge_configs(result[key], value)
            else:
                result[key] = value
                
        return result

    def _apply_environment_variables(self, config: Dict) -> Dict:
        """
        Override configuration with environment variables.

        Args:
            config: Current configuration

        Returns:
            Dict: Configuration with environment variables applied
        """
        env_mapping = {
            'BROWSER_NAME': ('browser', 'name'),
            'BROWSER_HEADLESS': ('browser', 'headless'),
            'BROWSER_WINDOW_WIDTH': ('browser', 'window_size', 0),
            'BROWSER_WINDOW_HEIGHT': ('browser', 'window_size', 1),
            'IMPLICIT_WAIT': ('browser', 'implicit_wait'),
            'PAGE_LOAD_TIMEOUT': ('browser', 'page_load_timeout'),
            'BASE_URL': ('test', 'base_url'),
            'SCREENSHOT_DIR': ('test', 'screenshot_dir'),
            'REPORT_DIR': ('test', 'report_dir'),
            'LOG_DIR': ('test', 'log_dir'),
            'RETRY_ATTEMPTS': ('test', 'retry_attempts'),
            'WAIT_TIMEOUT': ('test', 'wait_timeout')
        }

        for env_var, config_path in env_mapping.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                self._set_nested_value(config, config_path, self._convert_value(env_value))

        return config

    def _set_nested_value(self, config: Dict, path: tuple, value: Any):
        """
        Set a value in a nested dictionary using a path tuple.

        Args:
            config: Configuration dictionary
            path: Tuple of nested keys
            value: Value to set
        """
        current = config
        for key in path[:-1]:
            current = current.setdefault(key, {})
        
        if isinstance(current[path[-1]], tuple) and isinstance(value, (int, float)):
            # Handle window size tuple
            index = path[-1]
            size_list = list(current[path[-2]])
            size_list[index] = value
            current[path[-2]] = tuple(size_list)
        else:
            current[path[-1]] = value

    def _convert_value(self, value: str) -> Any:
        """
        Convert string value to appropriate type.

        Args:
            value: String value to convert

        Returns:
            Converted value
        """
        # Try converting to boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Try converting to integer
        try:
            return int(value)
        except ValueError:
            pass
        
        # Try converting to float
        try:
            return float(value)
        except ValueError:
            pass
        
        # Return as string
        return value

    def _create_config_objects(self, config: Dict) -> FrameworkConfig:
        """
        Create configuration objects from dictionary.

        Args:
            config: Configuration dictionary

        Returns:
            FrameworkConfig: Complete framework configuration

        Raises:
            ConfigurationError: If configuration is invalid
        """
        try:
            browser_config = BrowserConfig(
                name=config['browser']['name'],
                headless=config['browser']['headless'],
                window_size=tuple(config['browser']['window_size']),
                implicit_wait=config['browser']['implicit_wait'],
                page_load_timeout=config['browser']['page_load_timeout']
            )

            test_config = TestConfig(
                base_url=config['test']['base_url'],
                screenshot_dir=config['test']['screenshot_dir'],
                report_dir=config['test']['report_dir'],
                log_dir=config['test']['log_dir'],
                retry_attempts=config['test']['retry_attempts'],
                wait_timeout=config['test']['wait_timeout']
            )

            # Extract custom settings (anything not in browser or test configs)
            custom_settings = {
                k: v for k, v in config.items()
                if k not in {'browser', 'test'}
            }

            return FrameworkConfig(
                browser=browser_config,
                test=test_config,
                custom_settings=custom_settings
            )

        except KeyError as e:
            raise ConfigurationError(f"Missing required configuration key: {str(e)}")
        except Exception as e:
            raise ConfigurationError(f"Invalid configuration: {str(e)}")

    def get_browser_config(self) -> BrowserConfig:
        """Get browser configuration."""
        return self.config.browser

    def get_test_config(self) -> TestConfig:
        """Get test configuration."""
        return self.config.test

    def get_custom_setting(self, key: str, default: Any = None) -> Any:
        """
        Get a custom configuration setting.

        Args:
            key: Setting key
            default: Default value if key not found

        Returns:
            Setting value or default
        """
        return self.config.custom_settings.get(key, default)

    def to_dict(self) -> Dict:
        """
        Convert configuration to dictionary.

        Returns:
            Dict: Configuration as dictionary
        """
        return {
            'browser': {
                'name': self.config.browser.name,
                'headless': self.config.browser.headless,
                'window_size': self.config.browser.window_size,
                'implicit_wait': self.config.browser.implicit_wait,
                'page_load_timeout': self.config.browser.page_load_timeout
            },
            'test': {
                'base_url': self.config.test.base_url,
                'screenshot_dir': self.config.test.screenshot_dir,
                'report_dir': self.config.test.report_dir,
                'log_dir': self.config.test.log_dir,
                'retry_attempts': self.config.test.retry_attempts,
                'wait_timeout': self.config.test.wait_timeout
            },
            'custom_settings': self.config.custom_settings
        }