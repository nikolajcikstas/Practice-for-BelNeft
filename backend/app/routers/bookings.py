from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.auth import get_current_user_id
from app.config import settings
from app.database import get_db
from app.models.booking import Booking
from app.schemas import BookingCreate, BookingOut

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.get("", response_model=list[BookingOut])
def list_bookings(
    date: date = Query(..., description="Filter by date, format YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    from datetime import datetime, timedelta

    day_start = datetime.combine(date, datetime.min.time())
    day_end = day_start + timedelta(days=1)

    bookings = (
        db.query(Booking)
        .filter(Booking.start_time >= day_start, Booking.start_time < day_end)
        .order_by(Booking.start_time)
        .all()
    )
    return bookings


@router.post("", response_model=BookingOut, status_code=201)
def create_booking(
    data: BookingCreate,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    conflict = (
        db.query(Booking)
        .filter(
            Booking.start_time < data.end_time,
            Booking.end_time > data.start_time,
        )
        .first()
    )
    if conflict:
        raise HTTPException(
            status_code=409,
            detail=f"Time slot is already booked (booking id={conflict.id})",
        )

    booking = Booking(**data.model_dump())
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.delete("/{booking_id}", status_code=204)
def cancel_booking(
    booking_id: int,
    db: Session = Depends(get_db),
    user_id: int = Depends(get_current_user_id),
):
    booking = db.get(Booking, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")

    if booking.employee_id != user_id and user_id not in settings.admin_ids:
        raise HTTPException(status_code=403, detail="Not allowed to cancel this booking")

    db.delete(booking)
    db.commit()
