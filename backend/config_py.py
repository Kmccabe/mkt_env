"""
Configuration settings for the Market Simulation API.

This module manages all configuration using pydantic-settings for type safety
and environment variable support. Create a .env file to override defaults.

Example .env file:
    ENVIRONMENT=development
    MAX_BUYERS=200
    MAX_SELLERS=200
    DEFAULT_PORT=8002
    CORS_ORIGINS=["http://localhost:3000", "http://localhost:5173"]
"""

import os
from typing import List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Environment
    environment: str = Field(
        default="development",
        description="Application environment (development/staging/production)"
    )
    
    # Server settings
    default_port: int = Field(
        default=8001,
        ge=1000,
        le=65535,
        description="Default port for the API server"
    )
    
    # Market simulation limits
    max_buyers: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of buyers allowed in a simulation"
    )
    max_sellers: int = Field(
        default=100,
        ge=1,
        le=1000,
        description="Maximum number of sellers allowed in a simulation"
    )
    max_segments: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Maximum number of market segments allowed"
    )
    max_price: int = Field(
        default=1000,
        ge=1,
        description="Maximum price value allowed in simulations"
    )
    
    # Rate limiting
    rate_limit_requests: int = Field(
        default=30,
        ge=1,
        description="Number of requests allowed per minute"
    )
    
    # CORS settings
    cors_origins: List[str] = Field(
        default_factory=lambda: [
            "http://localhost:5173",
            "http://127.0.0.1:5173",
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ],
        description="Allowed CORS origins"
    )
    
    # Logging
    log_level: str = Field(
        default="INFO",
        description="Logging level (DEBUG/INFO/WARNING/ERROR)"
    )
    
    # API documentation
    api_title: str = Field(
        default="Market Simulation API",
        description="API title for documentation"
    )
    api_version: str = Field(
        default="2.1.0",
        description="API version"
    )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False
    }
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins based on environment."""
        if self.is_production:
            # In production, be more restrictive
            return [origin for origin in self.cors_origins 
                   if not ("localhost" in origin or "127.0.0.1" in origin)]
        return self.cors_origins


# Create global settings instance
settings = Settings()