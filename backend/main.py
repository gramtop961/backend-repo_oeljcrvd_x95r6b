from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from pydantic import EmailStr
from typing import List, Optional
from database import create_document, get_documents, get_document, update_document, delete_document
from schemas import Vehicle, MessageLead, OfferLead, ApplyOnline, SellTrade, CarFinder, TestDrive, Referral, ContactUs, Feedback
from email_utils import send_email
import base64

DEALER_NAME = "Best Deal Motors"
LEAD_TO_EMAIL = "bestdealmotors1626@gmail.com"

app = FastAPI(title=f"{DEALER_NAME} API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/test")
async def test():
    return {"status": "ok"}


# Inventory Endpoints
@app.get("/vehicles", response_model=List[Vehicle])
async def list_vehicles():
    docs = await get_documents("vehicle", {}, limit=500)
    return docs


@app.get("/vehicles/{vehicle_id}")
async def get_vehicle(vehicle_id: str):
    doc = await get_document("vehicle", {"id": vehicle_id})
    if not doc:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return doc


@app.post("/vehicles")
async def create_vehicle(vehicle: Vehicle):
    doc = await create_document("vehicle", vehicle.dict())
    return doc


@app.put("/vehicles/{vehicle_id}")
async def update_vehicle(vehicle_id: str, vehicle: Vehicle):
    updated = await update_document("vehicle", {"id": vehicle_id}, vehicle.dict())
    if not updated:
        raise HTTPException(status_code=404, detail="Vehicle not found")
    return updated


@app.delete("/vehicles/{vehicle_id}")
async def remove_vehicle(vehicle_id: str):
    ok = await delete_document("vehicle", {"id": vehicle_id})
    return {"deleted": ok}


# File uploads for Sell/Trade
@app.post("/sell-trade")
async def sell_trade(
    name: str = Form(...),
    email: EmailStr = Form(...),
    phone: str = Form(...),
    zip: str = Form(...),
    year: int = Form(...),
    make: str = Form(...),
    model: str = Form(...),
    trim: Optional[str] = Form(None),
    mileage: int = Form(...),
    vin: Optional[str] = Form(None),
    condition: Optional[str] = Form(None),
    payoff_info: Optional[str] = Form(None),
    files: List[UploadFile] = File([]),
):
    attachments = []
    file_refs: List[dict] = []
    for f in files:
        content = await f.read()
        # log snippet of base64 for debug, attach full file to email
        encoded_snippet = base64.b64encode(content).decode("utf-8")[:64] + "..."
        file_refs.append({"filename": f.filename, "content_type": f.content_type, "base64": encoded_snippet})
        attachments.append((f.filename, content, f.content_type or "application/octet-stream"))

    data = {
        "name": name,
        "email": str(email),
        "phone": phone,
        "zip": zip,
        "year": year,
        "make": make,
        "model": model,
        "trim": trim,
        "mileage": mileage,
        "vin": vin,
        "condition": condition,
        "payoff_info": payoff_info,
        "files": file_refs,
        "subject": "Sell or Trade Lead",
    }
    await create_document("lead", data)

    html = f"""
    <h2>Sell or Trade Lead</h2>
    <p><b>Name:</b> {name}<br/>
    <b>Email:</b> {email}<br/>
    <b>Phone:</b> {phone}<br/>
    <b>ZIP:</b> {zip}</p>
    <h3>Vehicle</h3>
    <p><b>{year} {make} {model} {trim or ''}</b><br/>
    Mileage: {mileage}<br/>
    VIN: {vin or '-'}<br/>
    Condition: {condition or '-'}<br/>
    Payoff: {payoff_info or '-'}
    </p>
    <p>Files attached: {len(attachments)}</p>
    """
    await send_email("Sell or Trade Lead", html, attachments)

    return {"status": "received"}


# Simple lead endpoints (store + email)
@app.post("/message")
async def message_lead(payload: MessageLead):
    data = {**payload.dict(), "subject": "Message Us Lead"}
    await create_document("lead", data)
    html = f"""
    <h2>Message Us Lead</h2>
    <p><b>Name:</b> {payload.name}<br/>
    <b>Email:</b> {payload.email}<br/>
    <b>Phone:</b> {payload.phone}</p>
    <p><b>Message:</b><br/>{payload.message or ''}</p>
    <p>Vehicle ID: {payload.vehicle_id or '-'} | Trade-in: {payload.trade_in}</p>
    """
    await send_email("Message Us Lead", html)
    return {"ok": True}


@app.post("/offer")
async def offer_lead(payload: OfferLead):
    data = {**payload.dict(), "subject": "Make an Offer Lead"}
    await create_document("lead", data)
    html = f"""
    <h2>Make an Offer Lead</h2>
    <p><b>Name:</b> {payload.name}<br/>
    <b>Email:</b> {payload.email}<br/>
    <b>Phone:</b> {payload.phone}<br/>
    <b>Offer:</b> ${payload.offer_amount:,.2f}<br/>
    Vehicle ID: {payload.vehicle_id or '-'}
    </p>
    """
    await send_email("Make an Offer Lead", html)
    return {"ok": True}


@app.post("/apply")
async def apply_online(payload: ApplyOnline):
    data = {**payload.dict(), "subject": "Apply Online Lead"}
    await create_document("lead", data)
    html = """
    <h2>Apply Online Lead</h2>
    <p>Your finance application has been submitted. Details are attached in the admin database.</p>
    """
    await send_email("Apply Online Lead", html)
    return {"ok": True}


@app.post("/car-finder")
async def car_finder(payload: CarFinder):
    data = {**payload.dict(), "subject": "Car Finder Lead"}
    await create_document("lead", data)
    html = f"""
    <h2>Car Finder Lead</h2>
    <p><b>Name:</b> {payload.name}<br/>
    <b>Email:</b> {payload.email}<br/>
    <b>Phone:</b> {payload.phone}</p>
    <p><b>Criteria:</b><br/>
    Year: {payload.year_min or ''}-{payload.year_max or ''}<br/>
    Make/Model: {payload.make or ''} {payload.model or ''}<br/>
    Body: {payload.body_style or ''}<br/>
    Mileage: {payload.mileage_min or ''}-{payload.mileage_max or ''}<br/>
    Price: {payload.price_min or ''}-{payload.price_max or ''}<br/>
    Notes: {payload.notes or ''}
    </p>
    """
    await send_email("Car Finder Lead", html)
    return {"ok": True}


@app.post("/test-drive")
async def test_drive(payload: TestDrive):
    data = {**payload.dict(), "subject": "Test Drive Lead"}
    await create_document("lead", data)
    html = f"""
    <h2>Test Drive Lead</h2>
    <p><b>Name:</b> {payload.name}<br/>
    <b>Email:</b> {payload.email}<br/>
    <b>Phone:</b> {payload.phone}<br/>
    <b>Preferred:</b> {payload.preferred_datetime}<br/>
    Vehicle: {payload.vehicle or '-'}<br/>
    Notes: {payload.notes or ''}
    </p>
    """
    await send_email("Test Drive Lead", html)
    return {"ok": True}


@app.post("/referral")
async def referral(payload: Referral):
    data = {**payload.dict(), "subject": "Referral Lead"}
    await create_document("lead", data)
    html = f"""
    <h2>Referral Lead</h2>
    <p><b>Your Name:</b> {payload.your_name} ({payload.your_phone}, {payload.your_email})<br/>
    <b>Friend:</b> {payload.friend_name} ({payload.friend_phone}, {payload.friend_email})<br/>
    Vehicle interest: {payload.interested_vehicle or '-'}
    </p>
    """
    await send_email("Referral Lead", html)
    return {"ok": True}


@app.post("/contact")
async def contact(payload: ContactUs):
    data = {**payload.dict(), "subject": "Contact Us Lead"}
    await create_document("lead", data)
    html = f"""
    <h2>Contact Us Lead</h2>
    <p><b>Name:</b> {payload.name}<br/>
    <b>Email:</b> {payload.email}<br/>
    <b>Phone:</b> {payload.phone}<br/>
    <b>Message:</b><br/>{payload.message}
    </p>
    """
    await send_email("Contact Us Lead", html)
    return {"ok": True}


@app.post("/feedback")
async def feedback(payload: Feedback):
    if payload.rating == 5:
        return {"ok": True, "public": True}
    await create_document("lead", {**payload.dict(), "subject": "Private Feedback"})
    html = f"""
    <h2>Private Feedback</h2>
    <p>Rating: {payload.rating}</p>
    <p>Name: {payload.name or '-'} | Phone: {payload.phone or '-'} | Email: {payload.email or '-'}</p>
    <p>{payload.comments or ''}</p>
    """
    await send_email("Private Feedback", html)
    return {"ok": True, "public": False}
