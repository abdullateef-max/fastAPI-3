from fastapi import APIRouter, HTTPException, Depends
from sqlmodel import Session, select
from app.models import Note
from app.database import get_session
from app.utils.backup import backup_notes_to_json

router = APIRouter()

@router.post("/", response_model=Note)
def create_note(note: Note, session: Session = Depends(get_session)):
    session.add(note)
    session.commit()
    session.refresh(note)
    
    # Backup notes to JSON after creating a new note
    backup_notes_to_json()
    
    return note

@router.get("/", response_model=list[Note])
def list_notes(session: Session = Depends(get_session)):
    notes = session.exec(select(Note)).all()
    return notes

@router.get("/{note_id}", response_model=Note)
def get_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.delete("/{note_id}")
def delete_note(note_id: int, session: Session = Depends(get_session)):
    note = session.get(Note, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    session.delete(note)
    session.commit()
    
    # Backup notes to JSON after deletion
    backup_notes_to_json()
    
    return {"message": "Note deleted successfully"}