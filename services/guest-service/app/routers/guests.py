from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

router = APIRouter()

# In-memory store (simulates a database)
guests_db: dict = {}
next_id = 1


class GuestCreate(BaseModel):
    name: str
    email: str
    phone: str
    nationality: Optional[str] = "Unknown"
    id_number: str


class GuestUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    nationality: Optional[str] = None


class GuestResponse(BaseModel):
    id: int
    name: str
    email: str
    phone: str
    nationality: str
    id_number: str
    created_at: str


@router.post("/", response_model=GuestResponse, status_code=201)
def create_guest(guest: GuestCreate):
    global next_id
    # Check duplicate email
    for g in guests_db.values():
        if g["email"] == guest.email:
            raise HTTPException(status_code=400, detail="Email already registered")
    
    new_guest = {
        "id": next_id,
        "name": guest.name,
        "email": guest.email,
        "phone": guest.phone,
        "nationality": guest.nationality,
        "id_number": guest.id_number,
        "created_at": datetime.now().isoformat()
    }
    guests_db[next_id] = new_guest
    next_id += 1
    return new_guest


@router.get("/", response_model=List[GuestResponse])
def get_all_guests():
    return list(guests_db.values())


@router.get("/{guest_id}", response_model=GuestResponse)
def get_guest(guest_id: int):
    if guest_id not in guests_db:
        raise HTTPException(status_code=404, detail="Guest not found")
    return guests_db[guest_id]


@router.put("/{guest_id}", response_model=GuestResponse)
def update_guest(guest_id: int, update: GuestUpdate):
    if guest_id not in guests_db:
        raise HTTPException(status_code=404, detail="Guest not found")
    guest = guests_db[guest_id]
    if update.name:
        guest["name"] = update.name
    if update.phone:
        guest["phone"] = update.phone
    if update.nationality:
        guest["nationality"] = update.nationality
    return guest


@router.delete("/{guest_id}")
def delete_guest(guest_id: int):
    if guest_id not in guests_db:
        raise HTTPException(status_code=404, detail="Guest not found")
    del guests_db[guest_id]
    return {"message": f"Guest {guest_id} deleted successfully"}
