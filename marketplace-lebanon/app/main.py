from datetime import datetime
from pathlib import Path
from typing import Optional, List

from fastapi import FastAPI, Request, Depends, Form, UploadFile, File, HTTPException, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlmodel import Session, select

from .database import init_db, get_session
from .models import User, Listing, Message, Currency, Category, Condition
from .auth import get_current_user, login_user, logout_user, create_user

PROJECT_ROOT = Path(__file__).resolve().parent
UPLOADS_DIR = PROJECT_ROOT / "static" / "uploads"
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="Lebanese Student Marketplace")

app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "static")), name="static")

templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))


@app.on_event("startup")
def on_startup() -> None:
    init_db()


@app.get("/", response_class=HTMLResponse)
def index(
    request: Request,
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user),
    q: Optional[str] = None,
    university: Optional[str] = None,
    category: Optional[Category] = None,
    currency: Optional[Currency] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
):
    statement = select(Listing).where(Listing.is_active == True).order_by(Listing.created_at.desc())
    if q:
        statement = statement.where((Listing.title.ilike(f"%{q}%")) | (Listing.description.ilike(f"%{q}%")))
    if university:
        statement = statement.where(Listing.university == university)
    if category:
        statement = statement.where(Listing.category == category)
    if currency:
        statement = statement.where(Listing.currency == currency)
    if min_price is not None:
        statement = statement.where(Listing.price >= min_price)
    if max_price is not None:
        statement = statement.where(Listing.price <= max_price)

    listings: List[Listing] = session.exec(statement).all()
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "user": current_user,
            "listings": listings,
            "filters": {
                "q": q or "",
                "university": university or "",
                "category": category.name if category else "",
                "currency": currency.name if currency else "",
                "min_price": min_price if min_price is not None else "",
                "max_price": max_price if max_price is not None else "",
            },
            "universities": User.UNIVERSITIES,
            "categories": [c for c in Category],
            "currencies": [c for c in Currency],
        },
    )


@app.get("/listing/{listing_id}", response_class=HTMLResponse)
def listing_detail(
    listing_id: int,
    request: Request,
    session: Session = Depends(get_session),
    current_user: Optional[User] = Depends(get_current_user),
):
    listing = session.get(Listing, listing_id)
    if not listing or not listing.is_active:
        raise HTTPException(status_code=404, detail="Listing not found")
    return templates.TemplateResponse(
        "listing_detail.html",
        {"request": request, "user": current_user, "listing": listing},
    )


@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request, current_user: Optional[User] = Depends(get_current_user)):
    if current_user:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login")
def login_submit(
    email: str = Form(...),
    password: str = Form(...),
):
    user = login_user(email=email, password=password)
    if not user:
        return RedirectResponse("/login?error=Invalid+credentials", status_code=status.HTTP_302_FOUND)
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    logout_user(response)
    response = login_user(email=email, password=password, create_response=response)
    return response


@app.post("/logout")
def logout():
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    logout_user(response)
    return response


@app.get("/signup", response_class=HTMLResponse)
def signup_page(request: Request, current_user: Optional[User] = Depends(get_current_user)):
    if current_user:
        return RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("signup.html", {"request": request, "universities": User.UNIVERSITIES})


@app.post("/signup")
def signup_submit(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    university: str = Form(...),
):
    try:
        user = create_user(name=name, email=email, password=password, university=university)
    except ValueError as ex:
        return RedirectResponse(f"/signup?error={str(ex).replace(' ', '+')}", status_code=status.HTTP_302_FOUND)
    response = RedirectResponse("/", status_code=status.HTTP_302_FOUND)
    response = login_user(email=user.email, password=password, create_response=response)
    return response


@app.get("/new-listing", response_class=HTMLResponse)
def new_listing_page(
    request: Request,
    current_user: User = Depends(get_current_user),
):
    if not current_user:
        return RedirectResponse("/login?error=Please+login", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "new_listing.html",
        {
            "request": request,
            "user": current_user,
            "categories": [c for c in Category],
            "currencies": [c for c in Currency],
        },
    )


@app.post("/new-listing")
async def new_listing_submit(
    title: str = Form(...),
    description: str = Form(...),
    price: float = Form(...),
    currency: Currency = Form(...),
    category: Category = Form(...),
    condition: Condition = Form(...),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not current_user:
        return RedirectResponse("/login?error=Please+login", status_code=status.HTTP_302_FOUND)

    image_path: Optional[str] = None
    if image and image.filename:
        safe_name = f"{int(datetime.utcnow().timestamp())}_{image.filename.replace(' ', '_')}"
        dest = UPLOADS_DIR / safe_name
        with dest.open("wb") as f:
            f.write(await image.read())
        image_path = f"/static/uploads/{safe_name}"

    listing = Listing(
        title=title.strip(),
        description=description.strip(),
        price=price,
        currency=currency,
        category=category,
        condition=condition,
        university=current_user.university,
        seller_id=current_user.id,
        image_path=image_path,
        created_at=datetime.utcnow(),
        is_active=True,
    )
    session.add(listing)
    session.commit()
    session.refresh(listing)
    return RedirectResponse(f"/listing/{listing.id}", status_code=status.HTTP_302_FOUND)


@app.get("/my/listings", response_class=HTMLResponse)
def my_listings(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not current_user:
        return RedirectResponse("/login?error=Please+login", status_code=status.HTTP_302_FOUND)
    stmt = select(Listing).where(Listing.seller_id == current_user.id).order_by(Listing.created_at.desc())
    items = session.exec(stmt).all()
    return templates.TemplateResponse("my_listings.html", {"request": request, "user": current_user, "listings": items})


@app.post("/listing/{listing_id}/message")
def message_seller(
    listing_id: int,
    content: str = Form(...),
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not current_user:
        return RedirectResponse("/login?error=Please+login", status_code=status.HTTP_302_FOUND)
    listing = session.get(Listing, listing_id)
    if not listing or not listing.is_active:
        raise HTTPException(status_code=404, detail="Listing not found")
    if listing.seller_id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot message your own listing")
    message = Message(
        listing_id=listing.id,
        sender_id=current_user.id,
        recipient_id=listing.seller_id,
        content=content.strip(),
        created_at=datetime.utcnow(),
    )
    session.add(message)
    session.commit()
    return RedirectResponse(f"/listing/{listing_id}?sent=1", status_code=status.HTTP_302_FOUND)


@app.get("/messages", response_class=HTMLResponse)
def inbox(
    request: Request,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    if not current_user:
        return RedirectResponse("/login?error=Please+login", status_code=status.HTTP_302_FOUND)
    stmt = select(Message).where(Message.recipient_id == current_user.id).order_by(Message.created_at.desc())
    messages = session.exec(stmt).all()
    return templates.TemplateResponse("messages.html", {"request": request, "user": current_user, "messages": messages})


@app.get("/healthz")
def healthz():
    return {"ok": True}