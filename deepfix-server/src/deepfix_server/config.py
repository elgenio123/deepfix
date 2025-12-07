import os
from typing import Dict, List, Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, field_validator


class PortalConfig(BaseModel):
    """Configuration for portal-based authorization."""

    base_url: str = Field(
        default="http://localhost:5000",
        description="Base URL for deepfix-portal backend",
    )
    validate_path: str = Field(
        default="/api/api-keys/validate",
        description="Path for API key validation endpoint",
    )
    service_token: str = Field(
        default="dev-portal-service-token",
        description="Shared token for server-to-portal validation requests",
    )
    timeout_seconds: float = Field(
        default=5.0, description="HTTP timeout when calling the portal"
    )

    @classmethod
    def load_from_env(cls, env_file: Optional[str] = None) -> "PortalConfig":
        """Load portal configuration from environment variables.

        Reads:
        - DEEPFIX_PORTAL_BASE_URL
        - DEEPFIX_PORTAL_VALIDATE_PATH
        - DEEPFIX_PORTAL_SERVICE_TOKEN
        - DEEPFIX_PORTAL_TIMEOUT_SECONDS
        """
        if env_file is not None:
            load_dotenv(env_file)
        base_url = os.getenv("DEEPFIX_PORTAL_BASE_URL", "http://localhost:5041")
        validate_path = os.getenv(
            "DEEPFIX_PORTAL_VALIDATE_PATH", "/api/api-keys/validate"
        )
        service_token = os.getenv("DEEPFIX_PORTAL_SERVICE_TOKEN")
        timeout_seconds = float(os.getenv("DEEPFIX_PORTAL_TIMEOUT_SECONDS", "5"))
        if not service_token:
            raise ValueError("DEEPFIX_PORTAL_SERVICE_TOKEN must be set")
        return cls(
            base_url=base_url,
            validate_path=validate_path,
            service_token=service_token,
            timeout_seconds=timeout_seconds,
        )


class PromptConfig(BaseModel):
    """Configuration for prompt generation.

    Attributes:
        custom_instructions: Optional custom instructions to append to prompts.
        dataset_analysis: Whether to include dataset analysis in prompts.
            Defaults to True.
        training_results_analysis: Whether to include training results analysis
            in prompts. Defaults to False.
    """

    custom_instructions: Optional[str] = Field(
        default=None, description="Custom instructions to append to created prompts"
    )
    dataset_analysis: bool = Field(
        default=True, description="Whether to analyze the dataset"
    )
    training_results_analysis: bool = Field(
        default=False, description="Whether to analyze the training"
    )


class LLMConfig(BaseModel):
    """Configuration for LLM provider settings.

    Attributes:
        api_key: Optional API key for the LLM provider.
        base_url: Optional base URL for the LLM API endpoint.
        model_name: Name of the LLM model to use.
        temperature: Sampling temperature for text generation. Defaults to 0.7.
        max_tokens: Maximum number of tokens to generate. Defaults to 8000.
        cache: Whether to cache LLM requests. Defaults to True.
        track_usage: Whether to track LLM usage. Defaults to True.
    """

    api_key: Optional[str] = Field(
        default=None, description="API key for the LLM provider"
    )
    base_url: Optional[str] = Field(
        default=None, description="Base URL for the LLM API"
    )
    model_name: str = Field(default=None, description="Model name to use for the LLM")
    temperature: float = Field(
        default=0.7, description="Sampling temperature for text generation"
    )
    max_tokens: int = Field(
        default=8000, description="Maximum tokens to generate in the response"
    )
    cache: bool = Field(default=True, description="Cache request")
    track_usage: bool = Field(default=True, description="Track usage")

    @classmethod
    def load_from_env(cls, env_file: Optional[str] = None) -> "LLMConfig":
        """Load LLM configuration from environment variables.

        Reads the following environment variables:
        - DEEPFIX_LLM_API_KEY
        - DEEPFIX_LLM_BASE_URL
        - DEEPFIX_LLM_MODEL_NAME
        - DEEPFIX_LLM_TEMPERATURE
        - DEEPFIX_LLM_MAX_TOKENS
        - DEEPFIX_LLM_CACHE
        - DEEPFIX_LLM_TRACK_USAGE

        Args:
            env_file: Optional path to .env file to load.

        Returns:
            LLMConfig instance populated from environment variables.
        """
        if env_file is not None:
            load_dotenv(env_file)
        api_key = os.getenv("DEEPFIX_LLM_API_KEY")
        base_url = os.getenv("DEEPFIX_LLM_BASE_URL")
        model_name = os.getenv("DEEPFIX_LLM_MODEL_NAME")
        temperature = float(os.getenv("DEEPFIX_LLM_TEMPERATURE"))
        max_tokens = int(os.getenv("DEEPFIX_LLM_MAX_TOKENS"))
        cache = bool(os.getenv("DEEPFIX_LLM_CACHE"))
        track_usage = bool(os.getenv("DEEPFIX_LLM_TRACK_USAGE"))
        return cls(
            api_key=api_key,
            base_url=base_url,
            model_name=model_name,
            temperature=temperature,
            max_tokens=max_tokens,
            cache=cache,
            track_usage=track_usage,
        )


class OutputConfig(BaseModel):
    """Configuration for output management.

    Attributes:
        save_prompt: Whether to save generated prompts to disk. Defaults to False.
        save_response: Whether to save AI responses to disk. Defaults to True.
        output_dir: Directory to save outputs. Defaults to "deepfix_output".
        format: Output format. Must be one of: txt, json, yaml. Defaults to "txt".
    """

    save_prompt: bool = Field(
        default=False, description="Whether to save generated prompts"
    )
    save_response: bool = Field(
        default=True, description="Whether to save AI responses"
    )
    output_dir: str = Field(
        default="deepfix_output",
        description="Directory to save outputs",
    )
    format: str = Field(default="txt", description="Output format (txt, json, yaml)")

    @field_validator("format")
    @classmethod
    def validate_format(cls, v):
        """Validate output format.

        Args:
            v: Format string to validate.

        Returns:
            Lowercased format string if valid.

        Raises:
            ValueError: If format is not one of: txt, json, yaml.
        """
        allowed_formats = ["txt", "json", "yaml"]
        if v.lower() not in allowed_formats:
            raise ValueError(f"format must be one of {allowed_formats}")
        return v.lower()


class TrainingDynamicsConfig(BaseModel):
    """Configuration for training dynamics analysis.

    Attributes:
        enabled_analyzers: List of analyzer names to enable. Defaults to:
            ["overfitting_detection", "training_stability", "gradient_analysis",
            "performance_trends"].
        overfitting_thresholds: Dictionary of thresholds for overfitting detection.
            Keys: train_val_divergence, val_loss_plateau_epochs, early_stopping_patience.
        stability_thresholds: Dictionary of thresholds for stability analysis.
            Keys: loss_variance_threshold, metric_volatility_window,
            gradient_norm_std_threshold.
        gradient_thresholds: Dictionary of thresholds for gradient analysis.
            Keys: exploding_gradient_threshold, vanishing_gradient_threshold,
            gradient_clip_threshold.
        lightweight_mode: Enable lightweight mode with <10% overhead. Defaults to True.
        max_analysis_time: Maximum analysis time in seconds. Defaults to 30.0.
        small_model_optimized: Optimize for models <100M parameters. Defaults to True.
    """

    # Analysis Configuration
    enabled_analyzers: List[str] = [
        "overfitting_detection",
        "training_stability",
        "gradient_analysis",
        "performance_trends",
    ]

    # Detection Thresholds
    overfitting_thresholds: Dict[str, float] = {
        "train_val_divergence": 0.1,  # Relative divergence threshold
        "val_loss_plateau_epochs": 5,  # Epochs for plateau detection
        "early_stopping_patience": 10,  # Patience for early stopping recommendation
    }

    stability_thresholds: Dict[str, float] = {
        "loss_variance_threshold": 0.05,  # Coefficient of variation threshold
        "metric_volatility_window": 10,  # Window size for volatility analysis
        "gradient_norm_std_threshold": 2.0,  # Standard deviation threshold for gradient norms
    }

    gradient_thresholds: Dict[str, float] = {
        "exploding_gradient_threshold": 10.0,  # Gradient norm threshold
        "vanishing_gradient_threshold": 1e-6,  # Minimum gradient norm
        "gradient_clip_threshold": 1.0,  # Recommended gradient clipping value
    }

    # Performance Configuration
    lightweight_mode: bool = True  # <10% overhead constraint
    max_analysis_time: float = 30.0  # Maximum analysis time in seconds
    small_model_optimized: bool = True  # Optimized for <100M parameters
