from datetime import date, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload

from app.auth import get_current_user_id
from app.config import settings
from app.database import get_db
from app.formatters import format_employee_name
from app.models.booking import Booking
from app.schemas import BookingCreate, BookingOut

router = APIRouter(prefix="/bookings", tags=["bookings"])


def _booking_out(booking: Booking) -> BookingOut:
    emp = booking.employee
    return BookingOut(
        id=booking.id,
        employee_id=booking.employee_id,
        employee_name=format_employee_name(
            emp.last_name, emp.first_name, emp.middle_name
        ) if emp else None,
        employee_photo_url=emp.photo_url if emp else None,
        topic=booking.topic,
        start_time=booking.start_time,
        end_time=booking.end_time,
    )


@router.get("", response_model=list[BookingOut])
def list_bookings(
    date: date | None = Query(None, description="Filter by single day YYYY-MM-DD"),
    from_date: date | None = Query(None, description="Range start YYYY-MM-DD"),
    to_date: date | None = Query(None, description="Range end YYYY-MM-DD"),
    db: Session = Depends(get_db),
):
    if from_date and to_date:
        day_start = datetime.combine(from_date, datetime.min.time())
        day_end = datetime.combine(to_date + timedelta(days=1), datetime.min.time())
    elif date:
        day_start = datetime.combine(date, datetime.min.time())
        day_end = day_start + timedelta(days=1)
    else:
        raise HTTPException(status_code=400, detail="Provide date or from_date+to_date")

    bookings = (
        db.query(Booking)
        .options(joinedload(Booking.employee))
        .filter(Booking.start_time >= day_start, Booking.start_time < day_end)
        .order_by(Booking.start_time)
        .all()
    )
    return [_booking_out(b) for b in bookings]


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
    booking = (
        db.query(Booking)
        .options(joinedload(Booking.employee))
        .filter(Booking.id == booking.id)
        .first()
    )
    return _booking_out(booking)


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
