from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from . import auth, crud, database, models, schemas


@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    yield


database.init_db()
app = FastAPI(title="Personal Network Tracker", lifespan=lifespan)
security = HTTPBearer()


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> int:
    user_id = auth.verify_token(credentials.credentials)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user_id


@app.post("/auth/signup", response_model=schemas.Token)
def signup(payload: schemas.UserCreate) -> schemas.Token:
    with database.get_session() as session:
        user = auth.create_user(session, payload.username, payload.password)
        if not user:
            raise HTTPException(status_code=400, detail="Username already exists")
        token = auth.create_access_token(user.id)
        return schemas.Token(access_token=token, token_type="bearer")


@app.post("/auth/login", response_model=schemas.Token)
def login(payload: schemas.UserCreate) -> schemas.Token:
    with database.get_session() as session:
        user = auth.authenticate_user(session, payload.username, payload.password)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        token = auth.create_access_token(user.id)
        return schemas.Token(access_token=token, token_type="bearer")


@app.get("/auth/me", response_model=schemas.UserRead)
def get_me(user_id: int = Depends(get_current_user)) -> schemas.UserRead:
    with database.get_session() as session:
        user = session.get(models.User, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user


@app.get("/contacts", response_model=list[schemas.ContactListRead])
def list_contacts(tag: str | None = None, user_id: int = Depends(get_current_user)) -> list[schemas.ContactListRead]:
    return crud.get_contacts(user_id, tag=tag)


@app.post("/contacts", response_model=schemas.ContactListRead)
def add_contact(payload: schemas.ContactCreate, user_id: int = Depends(get_current_user)) -> schemas.ContactListRead:
    contact = models.Contact.model_validate(payload, update={"user_id": user_id})
    return crud.create_contact(contact)


@app.get("/contacts/{contact_id}", response_model=schemas.ContactRead)
def get_contact(contact_id: int, user_id: int = Depends(get_current_user)) -> schemas.ContactRead:
    contact = crud.get_contact(user_id, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@app.put("/contacts/{contact_id}", response_model=schemas.ContactListRead)
def update_contact(contact_id: int, payload: schemas.ContactCreate, user_id: int = Depends(get_current_user)) -> schemas.ContactListRead:
    updated = crud.update_contact(
        user_id,
        contact_id,
        name=payload.name,
        title=payload.title,
        company=payload.company,
        email=payload.email,
        phone=payload.phone,
        tags=payload.tags,
        priority=payload.priority,
        notes=payload.notes,
    )
    if not updated:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated


@app.delete("/contacts/{contact_id}")
def delete_contact(contact_id: int, user_id: int = Depends(get_current_user)) -> dict:
    success = crud.delete_contact(user_id, contact_id)
    if not success:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"message": "Contact deleted"}


@app.post("/contacts/{contact_id}/interactions", response_model=schemas.InteractionRead)
def add_interaction(contact_id: int, payload: schemas.InteractionCreate, user_id: int = Depends(get_current_user)) -> schemas.InteractionRead:
    contact = crud.get_contact(user_id, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    
    interaction = models.Interaction.model_validate(
        payload,
        update={
            "contact_id": contact_id,
            "date": payload.date or datetime.now(timezone.utc),
        },
    )
    try:
        return crud.create_interaction(contact_id, interaction)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/contacts/{contact_id}/interactions", response_model=list[schemas.InteractionRead])
def list_interactions(contact_id: int, user_id: int = Depends(get_current_user)) -> list[schemas.InteractionRead]:
    contact = crud.get_contact(user_id, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return crud.get_interactions(user_id, contact_id)


@app.put("/contacts/{contact_id}/interactions/{interaction_id}", response_model=schemas.InteractionRead)
def update_interaction(contact_id: int, interaction_id: int, payload: schemas.InteractionCreate, user_id: int = Depends(get_current_user)) -> schemas.InteractionRead:
    interaction = crud.update_interaction(
        user_id,
        contact_id,
        interaction_id,
        type=payload.type,
        channel=payload.channel,
        notes=payload.notes,
        follow_up=payload.follow_up,
        follow_up_notes=payload.follow_up_notes,
        date=payload.date or datetime.now(timezone.utc),
    )
    if not interaction:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return interaction


@app.delete("/contacts/{contact_id}/interactions/{interaction_id}")
def remove_interaction(contact_id: int, interaction_id: int, user_id: int = Depends(get_current_user)) -> dict:
    success = crud.delete_interaction(user_id, contact_id, interaction_id)
    if not success:
        raise HTTPException(status_code=404, detail="Interaction not found")
    return {"message": "Interaction deleted"}
