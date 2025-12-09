"""
SQLAlchemy database models for deepfix-server.

Re-exports models from deepfix_core for use in the server.
"""
from deepfix_core.models import DatabaseBase as Base
from deepfix_core.models import RequestLog

__all__ = ["Base", "RequestLog"]
