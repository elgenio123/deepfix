"""
SQLAlchemy database models shared across deepfix packages.
"""

import uuid
from datetime import datetime
from sqlalchemy import Column, DateTime, Float, Integer, String, Text, text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class RequestLog(Base):
    """Request/Response log from deepfix-server.

    Stores successful API requests with user identity, request/response payloads,
    and timing information.

    Attributes:
        id: Unique identifier for the log entry.
        user_id: ID of the user who made the request.
        user_email: Email of the user who made the request.
        endpoint: API endpoint that was called.
        request_json: JSON-serialized request payload.
        response_json: JSON-serialized response payload.
        status_code: HTTP status code of the response.
        duration_ms: Request duration in milliseconds.
        created_at: Timestamp when the log entry was created.
    """

    __tablename__ = "request_logs"

    id = Column(
        String,
        primary_key=True,
        default=lambda: str(
            f"req_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4()}"
        ),
    )
    user_id = Column(String, nullable=False, index=True)
    user_email = Column(String, nullable=False)
    endpoint = Column(String, nullable=False)
    request_json = Column(Text, nullable=True)
    response_json = Column(Text, nullable=True)
    status_code = Column(Integer, nullable=True)
    duration_ms = Column(Float, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
