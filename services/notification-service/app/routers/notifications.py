from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

router = APIRouter()

notifications_db: dict = {}
next_id = 1


class NotificationType(str, Enum):
    booking_confirmed = "Booking Confirmed"
    booking_cancelled = "Booking Cancelled"
    payment_received = "Payment Received"
    check_in_reminder = "Check-In Reminder"
    check_out_reminder = "Check-Out Reminder"


class NotificationChannel(str, Enum):
    email = "Email"
    sms = "SMS"
    both = "Both"


class NotificationCreate(BaseModel):
    guest_id: int
    booking_id: int
    notification_type: NotificationType
    channel: NotificationChannel
    recipient_email: Optional[str] = ""
    recipient_phone: Optional[str] = ""
    custom_message: Optional[str] = ""


class NotificationResponse(BaseModel):
    id: int
    guest_id: int
    booking_id: int
    notification_type: str
    channel: str
    recipient_email: str
    recipient_phone: str
    message: str
    status: str
    sent_at: str


def build_message(notification_type: str, booking_id: int, custom: str) -> str:
    templates = {
        "Booking Confirmed": f"Your booking #{booking_id} has been confirmed. We look forward to welcoming you!",
        "Booking Cancelled": f"Your booking #{booking_id} has been cancelled. We hope to see you again soon.",
        "Payment Received": f"Payment for booking #{booking_id} has been received. Thank you!",
        "Check-In Reminder": f"Reminder: Your check-in for booking #{booking_id} is tomorrow. See you soon!",
        "Check-Out Reminder": f"Reminder: Your check-out for booking #{booking_id} is tomorrow. We hope you enjoyed your stay!"
    }
    return custom if custom else templates.get(notification_type, "Notification from Grand Hotel.")


@router.post("/send", response_model=NotificationResponse, status_code=201)
def send_notification(notification: NotificationCreate):
    global next_id
    message = build_message(notification.notification_type.value, notification.booking_id, notification.custom_message)
    
    new_notif = {
        "id": next_id,
        "guest_id": notification.guest_id,
        "booking_id": notification.booking_id,
        "notification_type": notification.notification_type.value,
        "channel": notification.channel.value,
        "recipient_email": notification.recipient_email,
        "recipient_phone": notification.recipient_phone,
        "message": message,
        "status": "Sent",
        "sent_at": datetime.now().isoformat()
    }
    notifications_db[next_id] = new_notif
    next_id += 1
    return new_notif


@router.get("/", response_model=List[NotificationResponse])
def get_all_notifications():
    return list(notifications_db.values())


@router.get("/{notification_id}", response_model=NotificationResponse)
def get_notification(notification_id: int):
    if notification_id not in notifications_db:
        raise HTTPException(status_code=404, detail="Notification not found")
    return notifications_db[notification_id]


@router.get("/guest/{guest_id}", response_model=List[NotificationResponse])
def get_notifications_by_guest(guest_id: int):
    return [n for n in notifications_db.values() if n["guest_id"] == guest_id]


@router.get("/booking/{booking_id}", response_model=List[NotificationResponse])
def get_notifications_by_booking(booking_id: int):
    return [n for n in notifications_db.values() if n["booking_id"] == booking_id]
