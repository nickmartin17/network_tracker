from fastapi import FastAPI, HTTPException

from . import crud, database, models, schemas

app = FastAPI(title="Personal Network Tracker")


@app.on_event("startup")
def on_startup() -> None:
    database.init_db()


@app.get("/contacts", response_model=list[schemas.ContactRead])
def list_contacts(tag: str | None = None) -> list[schemas.ContactRead]:
    return crud.get_contacts(tag=tag)


@app.post("/contacts", response_model=schemas.ContactRead)
def add_contact(payload: schemas.ContactCreate) -> schemas.ContactRead:
    contact = models.Contact.from_orm(payload)
    return crud.create_contact(contact)


@app.get("/contacts/{contact_id}", response_model=schemas.ContactRead)
def get_contact(contact_id: int) -> schemas.ContactRead:
    contact = crud.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@app.post("/contacts/{contact_id}/interactions", response_model=schemas.InteractionRead)
def add_interaction(contact_id: int, payload: schemas.InteractionCreate) -> schemas.InteractionRead:
    interaction = models.Interaction.from_orm(payload)
    if payload.date is None:
        interaction.date = models.datetime.utcnow()
    try:
        return crud.create_interaction(contact_id, interaction)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.get("/contacts/{contact_id}/interactions", response_model=list[schemas.InteractionRead])
def list_interactions(contact_id: int) -> list[schemas.InteractionRead]:
    contact = crud.get_contact(contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return crud.get_interactions(contact_id)
