import json
from sqlmodel import select
from app.database import get_session
from app.models import Note

def backup_notes_to_json():
    with next(get_session()) as session:
        notes = session.exec(select(Note)).all()
        notes_data = [note.dict() for note in notes]
        
        # Convert datetime objects to strings for JSON serialization
        for note in notes_data:
            note["created_at"] = note["created_at"].isoformat()
        
        with open("notes.json", "w") as f:
            json.dump(notes_data, f, indent=2)