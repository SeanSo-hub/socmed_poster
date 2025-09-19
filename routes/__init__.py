from flask import Blueprint

# This package exposes three blueprints imported by the application:
# - main_bp: UI pages (index, post handler)
# - api_bp: JSON API endpoints (status, health)
# - utils_bp: utility routes (public uploads)

from .main import main_bp
from .api import api_bp
from .utils import utils_bp

__all__ = ["main_bp", "api_bp", "utils_bp"]
