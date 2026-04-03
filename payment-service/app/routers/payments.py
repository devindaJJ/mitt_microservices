from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

router = APIRouter()

payments_db: dict = {}
next_id = 1


class PaymentMethod(str, Enum):
    credit_card = "Credit Card"
    debit_card = "Debit Card"
    cash = "Cash"
    bank_transfer = "Bank Transfer"


class PaymentStatus(str, Enum):
    pending = "Pending"
    completed = "Completed"
    failed = "Failed"
    refunded = "Refunded"


class PaymentCreate(BaseModel):
    booking_id: int
    guest_id: int
    amount: float
    payment_method: PaymentMethod
    currency: Optional[str] = "USD"


class PaymentResponse(BaseModel):
    id: int
    booking_id: int
    guest_id: int
    amount: float
    currency: str
    payment_method: str
    status: str
    transaction_ref: str
    paid_at: str


@router.post("/", response_model=PaymentResponse, status_code=201)
def process_payment(payment: PaymentCreate):
    global next_id
    import random, string
    ref = "TXN-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=10))
    
    new_payment = {
        "id": next_id,
        "booking_id": payment.booking_id,
        "guest_id": payment.guest_id,
        "amount": payment.amount,
        "currency": payment.currency,
        "payment_method": payment.payment_method.value,
        "status": PaymentStatus.completed.value,
        "transaction_ref": ref,
        "paid_at": datetime.now().isoformat()
    }
    payments_db[next_id] = new_payment
    next_id += 1
    return new_payment


@router.get("/", response_model=List[PaymentResponse])
def get_all_payments():
    return list(payments_db.values())


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int):
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payments_db[payment_id]


@router.get("/booking/{booking_id}", response_model=List[PaymentResponse])
def get_payments_by_booking(booking_id: int):
    return [p for p in payments_db.values() if p["booking_id"] == booking_id]


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
def refund_payment(payment_id: int):
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment = payments_db[payment_id]
    if payment["status"] != PaymentStatus.completed.value:
        raise HTTPException(status_code=400, detail="Only completed payments can be refunded")
    payment["status"] = PaymentStatus.refunded.value
    return payment


@router.get("/{payment_id}/invoice")
def get_invoice(payment_id: int):
    if payment_id not in payments_db:
        raise HTTPException(status_code=404, detail="Payment not found")
    payment = payments_db[payment_id]
    return {
        "invoice_number": f"INV-{payment_id:05d}",
        "booking_id": payment["booking_id"],
        "guest_id": payment["guest_id"],
        "amount": payment["amount"],
        "currency": payment["currency"],
        "payment_method": payment["payment_method"],
        "transaction_ref": payment["transaction_ref"],
        "status": payment["status"],
        "issued_at": datetime.now().isoformat()
    }
