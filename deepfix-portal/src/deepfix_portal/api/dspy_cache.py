"""
Database-backed cache implementation for DSPy.

This module provides a custom cache that stores LLM request/response pairs
in the database with hit count tracking, following DSPy's cache customization patterns.
"""

import json
import logging
from datetime import datetime, timezone
from hashlib import sha256
from typing import Any, Dict, Optional

import dspy.clients
import orjson
from sqlalchemy.exc import IntegrityError

from .database import SessionLocal
from .models import DSPyCache

LOGGER = logging.getLogger(__name__)


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
        # We don't call super().__init__() because we're replacing the default cache
        # behavior entirely with our database implementation
        # pylint: disable=super-init-not-called
        LOGGER.info("Initialized DSPy database cache")

    def cache_key(
        self,
        request: Dict[str, Any],
        ignored_args_for_cache_key: list[str] = ["api_key", "api_base", "base_url"],
    ) -> str:
        """Compute cache key from request.

        The cache key is a SHA256 hash of the request parameters, excluding
        ignored arguments. Uses orjson for deterministic serialization with
        recursive key sorting to ensure identical requests always produce the
        same hash, regardless of dictionary key ordering.

        Args:
            request: The LLM request dictionary containing messages, model, etc.
            ignored_args_for_cache_key: Optional list of keys to ignore when
                computing the cache key. Defaults to ["api_key", "api_base", "base_url"].

        Returns:
            SHA256 hash string to use as cache key.
        """

        # Filter out ignored arguments from the request
        params = {
            k: v for k, v in request.items() if k not in ignored_args_for_cache_key
        }

        # Use orjson with OPT_SORT_KEYS for deterministic, recursive key sorting
        # This ensures that {"a": 1, "b": 2} and {"b": 2, "a": 1} produce the same hash
        cache_bytes = orjson.dumps(params, option=orjson.OPT_SORT_KEYS)
        return sha256(cache_bytes).hexdigest()

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
        key = self.cache_key(request, ignored_args_for_cache_key)
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
