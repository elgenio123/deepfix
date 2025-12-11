"""
Request logs routes for viewing API usage history.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import RequestLog, User
from ..schemas import (
    RequestLogListResponse,
    RequestLogResponse,
    RequestLogStatsResponse,
)

router = APIRouter()


@router.get("/", response_model=RequestLogListResponse)
async def list_request_logs(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    from_date: Optional[datetime] = Query(None, description="Filter from date"),
    to_date: Optional[datetime] = Query(None, description="Filter to date"),
    endpoint: Optional[str] = Query(None, description="Filter by endpoint"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    List all request logs for the current user with pagination.
    """
    # Base query filtered by user
    query = db.query(RequestLog).filter(RequestLog.user_id == current_user.id)

    # Apply date filters
    if from_date:
        query = query.filter(RequestLog.created_at >= from_date)
    if to_date:
        query = query.filter(RequestLog.created_at <= to_date)
    if endpoint:
        query = query.filter(RequestLog.endpoint == endpoint)

    # Get total count
    total = query.count()

    # Calculate pagination
    total_pages = (total + page_size - 1) // page_size if total > 0 else 1
    offset = (page - 1) * page_size

    # Get paginated results ordered by most recent first
    items = (
        query.order_by(RequestLog.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    return RequestLogListResponse(
        items=[RequestLogResponse.model_validate(item) for item in items],
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


@router.get("/stats", response_model=RequestLogStatsResponse)
async def get_request_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get usage statistics for the current user.
    """
    now = datetime.now(timezone.utc)
    day_ago = now - timedelta(days=1)
    week_ago = now - timedelta(days=7)
    month_ago = now - timedelta(days=30)

    # Base query for user
    base_query = db.query(RequestLog).filter(RequestLog.user_id == current_user.id)

    # Total requests
    total_requests = base_query.count()

    # Requests in last 24 hours
    total_requests_24h = base_query.filter(RequestLog.created_at >= day_ago).count()

    # Requests in last 7 days
    total_requests_7d = base_query.filter(RequestLog.created_at >= week_ago).count()

    # Requests in last 30 days
    total_requests_30d = base_query.filter(RequestLog.created_at >= month_ago).count()

    # Average duration
    avg_duration = (
        db.query(func.avg(RequestLog.duration_ms))
        .filter(RequestLog.user_id == current_user.id)
        .scalar()
    )

    # Endpoint breakdown
    endpoint_counts = (
        db.query(RequestLog.endpoint, func.count(RequestLog.id))
        .filter(RequestLog.user_id == current_user.id)
        .group_by(RequestLog.endpoint)
        .all()
    )
    endpoints = {endpoint: count for endpoint, count in endpoint_counts}

    return RequestLogStatsResponse(
        total_requests=total_requests,
        total_requests_24h=total_requests_24h,
        total_requests_7d=total_requests_7d,
        total_requests_30d=total_requests_30d,
        avg_duration_ms=round(avg_duration, 2) if avg_duration else None,
        endpoints=endpoints,
    )


@router.get("/{log_id}", response_model=RequestLogResponse)
async def get_request_log(
    log_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Get a specific request log by ID.
    """
    log = (
        db.query(RequestLog)
        .filter(RequestLog.id == log_id, RequestLog.user_id == current_user.id)
        .first()
    )

    if not log:
        raise HTTPException(status_code=404, detail="Request log not found")

    return log
