from core.config import config
from core.global_tts import GlobalTTS
from core.note import Note

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import os
from pathlib import Path

# Erstelle eine FastAPI App
app = FastAPI()

# Erstelle GlobalTTS Instanz separat
global_tts = GlobalTTS(config)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory="frontend"), name="static")

# Pydantic models
class CardAudioRequest(BaseModel):
    card_id: int
    language: str = "en"

@app.get("/")
async def read_index():
    return FileResponse('frontend/index.html')

@app.get("/api/decks")
async def get_decks():
    """Get all available Anki decks"""
    try:
        # Verwende AnkiConnect um alle Decks zu holen
        decks = global_tts.anki_connect.invoke('deckNames')
        
        # Hole Anzahl der Karten pro Deck
        deck_info = []
        for deck_name in decks:
            cards = global_tts.anki_connect.invoke('findCards', query=f'deck:"{deck_name}"')
            deck_info.append({
                "name": deck_name,
                "card_count": len(cards)
            })
        
        return deck_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/deck/{deck_name}/cards")
async def get_deck_cards(deck_name: str):
    """Get all cards from a specific deck"""
    try:
        # Finde alle Karten im Deck
        card_ids = global_tts.anki_connect.invoke('findCards', query=f'deck:"{deck_name}"')
        
        # Hole Detailinformationen für alle Karten
        cards_info = global_tts.anki_connect.invoke('cardsInfo', cards=card_ids[:100])  # Limit für Performance
        
        cards = []
        for card_info in cards_info:
            note_id = card_info['note']
            note = Note(note_id)
            
            # Prüfe ob Audio-Feld leer ist
            audio_field_content = note.get_field(note.note_type["audio_field"]) if note.note_type else ""
            has_audio = bool(audio_field_content and audio_field_content.strip())
            
            text_field = note.note_type["text_field"] if note.note_type else "Front"
            text_content = note.get_field(text_field) if note.note_type else ""
            
            cards.append({
                "id": card_info['cardId'],
                "note_id": note_id,
                "text": text_content,
                "note_type": note.note_info.get("modelName", "Unknown"),
                "has_audio": has_audio,
                "audio_content": audio_field_content
            })
        
        return {
            "deck_name": deck_name,
            "total_cards": len(card_ids),
            "loaded_cards": len(cards),
            "cards": cards
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-audio-for-card")
async def generate_audio_for_card(request: CardAudioRequest):
    """Generate audio for a specific card"""
    try:
        # Hole Card-Informationen
        card_info = global_tts.anki_connect.invoke('cardsInfo', cards=[request.card_id])[0]
        note_id = card_info['note']
        note = Note(note_id)
        
        # Hole Text aus der entsprechenden Feld
        text_field = note.note_type["text_field"] if note.note_type else "Front"
        text = note.get_field(text_field)
        
        if not text:
            raise HTTPException(status_code=400, detail="No text found in card")
        
        # Real TTS implementation example
        # Create audio directory if it doesn't exist
        audio_dir = Path("frontend/audio")
        audio_dir.mkdir(exist_ok=True)

        # Generate audio filename
        audio_filename = f"card_{request.card_id}_{request.language}.mp3"
        audio_path = audio_dir / audio_filename

        # Here you would call your actual TTS service
        # For example with gTTS:
        # from gtts import gTTS
        # tts = gTTS(text=text, lang=request.language)
        # tts.save(str(audio_path))

        # Or with pyttsx3:
        # import pyttsx3
        # engine = pyttsx3.init()
        # engine.save_to_file(text, str(audio_path))
        # engine.runAndWait()

        # Update the note in Anki
        # note.set_audio_field(f"[sound:{audio_filename}]")

        audio_url = f"/static/audio/{audio_filename}"
        
        return {
            "success": True,
            "card_id": request.card_id,
            "text": text,
            "language": request.language,
            "audio_url": audio_url,
            "audio_filename": audio_filename
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)