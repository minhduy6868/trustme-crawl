"""
Fact-Check API Package
"""

from .main import app
from .models import *
from .services import *

__version__ = "1.0.0"
__all__ = ["app"]
