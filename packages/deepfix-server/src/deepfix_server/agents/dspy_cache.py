"""
Database-backed cache implementation for DSPy.

This module provides a custom cache that stores LLM request/response pairs
in the database with hit count tracking, following DSPy's cache customization patterns.
"""

import copy
import json
import logging
import os
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import dspy.clients
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


LOGGER = logging.getLogger(__name__)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class DSPyCache(Base):
    """DSPy LLM cache model for database-backed caching"""

    __tablename__ = "dspy_cache"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    cache_key = Column(String, unique=True, nullable=False, index=True)  # SHA256 hash
    model_name = Column(String, nullable=False, index=True)  # LLM model identifier
    request_json = Column(Text, nullable=False)  # JSON serialized request
    response_json = Column(Text, nullable=False)  # JSON serialized response
    hit_count = Column(Integer, default=0, nullable=False)  # Number of cache hits
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class DSPyDatabaseCache(dspy.clients.Cache):
    """Database-backed cache for DSPy LLM calls.

    This cache stores LLM request/response pairs in a PostgreSQL database,
    keyed by a hash of the messages and model name. It tracks cache hit counts
    for analytics and uses database transactions for thread safety.

    Example:
        >>> cache = DSPyDatabaseCache()
        >>> dspy.cache = cache
        >>> # Now all DSPy LLM calls will use this cache
    """

    def __init__(self, **kwargs):  # pylint: disable=unused-argument
        """Initialize the database cache.

        Args:
            **kwargs: Additional arguments (for compatibility with base class).
                     Note: enable_disk_cache and enable_memory_cache are ignored
                     as this cache replaces those mechanisms.
        """
        super().__init__(
            enable_disk_cache=True,
            enable_memory_cache=False,
            disk_cache_dir=os.getenv("DSPY_CACHEDIR", ".dspy_cache"),
            disk_size_limit_bytes=1024 * 1024 * 10,
            memory_max_entries=1000000,
        )
        LOGGER.info("Initialized DSPy database cache")

    def get(
        self,
        request: Dict[str, Any],
        ignored_args_for_cache_key: Optional[list[str]] = None,
    ) -> Optional[Any]:
        """Retrieve cached response for a request.

        If a cache entry exists:
        - Increments the hit_count
        - Updates the updated_at timestamp
        - Returns the cached response

        Args:
            request: The LLM request dictionary.
            ignored_args_for_cache_key: Optional list of keys to ignore (not used).

        Returns:
            Cached response object if found, None otherwise.
        """
        try:
            key = self.cache_key(request, ignored_args_for_cache_key)
        except Exception:
            LOGGER.debug(f"Failed to generate cache key for request: {request}")
            return None

        if self.enable_disk_cache and key in self.disk_cache:
            response = self.disk_cache[key]
            response = copy.deepcopy(response)
            if hasattr(response, "usage"):
                # Clear the usage data when cache is hit, because no LM call is made
                response.usage = {}
                response.cache_hit = True
            return response

        db = SessionLocal()

        try:
            # Query for cache entry
            cache_entry = db.query(DSPyCache).filter(DSPyCache.cache_key == key).first()

            if cache_entry:
                # Cache hit - increment counter and update timestamp
                cache_entry.hit_count += 1
                cache_entry.updated_at = datetime.now(timezone.utc)
                db.commit()

                # Deserialize and return cached response
                response = json.loads(cache_entry.response_json)
                LOGGER.debug(
                    "Cache HIT for model=%s, hit_count=%s",
                    cache_entry.model_name,
                    cache_entry.hit_count,
                )
                if self.enable_disk_cache:
                    self.disk_cache[key] = response
                if hasattr(response, "usage"):
                    response.usage = {}
                    response.cache_hit = True
                return response

            # Cache miss
            LOGGER.debug("Cache MISS for key=%s...", key[:16])
            return None

        except Exception as exc:  # pylint: disable=broad-except
            db.rollback()
            LOGGER.warning("Error reading from cache: %s", exc)
            return None
        finally:
            db.close()

    def put(
        self,
        request: Dict[str, Any],
        value: Any,
        ignored_args_for_cache_key: Optional[list[str]] = None,
        enable_memory_cache: bool = True,  # Kept for compatibility
    ) -> None:
        """Store a response in the cache.

        Creates a new cache entry with:
        - cache_key: SHA256 hash of messages + model
        - model_name: Extracted from request
        - request_json: Serialized request
        - response_json: Serialized response
        - hit_count: Initialized to 0

        Args:
            request: The LLM request dictionary.
            value: The response to cache.
            ignored_args_for_cache_key: Optional list of keys to ignore (not used).
            enable_memory_cache: Ignored (kept for compatibility).
        """
        key = self.cache_key(request, ignored_args_for_cache_key)
        model_name = request.get("model", "unknown")

        if self.enable_disk_cache:
            try:
                self.disk_cache[key] = value
            except Exception as e:
                # Disk cache writing can fail for different reasons, e.g. disk full or the `value` is not picklable.
                LOGGER.debug(f"Failed to put value in disk cache: {value}, {e}")

        db = SessionLocal()
        try:
            # Check if entry already exists (race condition protection)
            existing = db.query(DSPyCache).filter(DSPyCache.cache_key == key).first()
            if existing:
                # Entry already exists, no need to insert again
                LOGGER.debug("Cache entry already exists for key=%s...", key[:16])
                return

            # Serialize request and response
            request_json = json.dumps(request, default=str)
            response_json = json.dumps(value, default=str)

            # Create new cache entry
            cache_entry = DSPyCache(
                cache_key=key,
                model_name=model_name,
                request_json=request_json,
                response_json=response_json,
                hit_count=0,
            )

            db.add(cache_entry)
            db.commit()

            LOGGER.debug(
                "Cached response for model=%s, key=%s...", model_name, key[:16]
            )

        except IntegrityError:
            # Race condition: another thread inserted the same key
            db.rollback()
            LOGGER.debug("Cache entry race condition for key=%s...", key[:16])
        except Exception as exc:  # pylint: disable=broad-except
            db.rollback()
            LOGGER.warning("Error writing to cache: %s", exc)
        finally:
            db.close()
