import json
import os
import logging
import requests
from typing import List
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.services.web_page_processor import WebPagePreprocessor
from src.services.pdf_processor import PDFPreprocessor
from src.services.chunk_processor import ChunkProcessor

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8765"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def process_input(input_path: str) -> List[str]:
    if input_path.startswith("http://") or input_path.startswith("https://"):
        logging.info("Processing web page...")
        preprocessor = WebPagePreprocessor(input_path)
        preprocessor.fetch_content()
        preprocessor.extract_text()
        preprocessor.chunk_text(max_tokens=1500)
        return preprocessor.get_chunks()
    elif input_path.lower().endswith(".pdf"):
        logging.info("Processing PDF...")
        preprocessor = PDFPreprocessor(input_path)
        preprocessor.extract_text()
        preprocessor.chunk_text(max_tokens=1500)
        return preprocessor.get_chunks()
    else:
        raise ValueError("Input must be a valid URL or a PDF file path.")
    
def request_permission(anki_connect_url: str) -> dict:
    payload = {
        "action": "requestPermission",
        "version": 6
    }
    try:
        response = requests.post(anki_connect_url, json=payload)
        return response.json()
    except requests.exceptions.RequestException as e:
        logging.error(f"Error requesting permission: {e}")
        return {"result": {"permission": "denied"}, "error": str(e)}

def add_note(deck_name: str, front: str, back: str, anki_connect_url: str) -> dict:
    permission_response = request_permission(anki_connect_url)
    if permission_response["result"]["permission"] != "granted":
        return {"error": "Permission denied by AnkiConnect"}

    payload = {
        "action": "addNote",
        "version": 6,
        "params": {
            "note": {
                "deckName": deck_name,
                "modelName": "Basic",
                "fields": {
                    "Front": front,
                    "Back": back
                },
                "tags": []
            }
        }
    }
    logging.info(f"Payload: {json.dumps(payload, indent=2)}")
    response = requests.post(anki_connect_url, json=payload)
    logging.info(f"AnkiConnect response: {response.json()}")
    return response.json()

# @app.post("/autonomous-anki-builder")
# async def autonomous_anki_builder(request: Request):
#     try:
#         req_body = await request.json()
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid JSON")

#     input_path = req_body.get('input_path')
#     deck_name = req_body.get('deck_name')

#     if not input_path or not deck_name:
#         raise HTTPException(status_code=400, detail="Please pass 'input_path' and 'deck_name' in the request body")

#     try:
#         chunks = process_input(input_path)
#         chunk_processor = ChunkProcessor(chunks)
#         flashcards = chunk_processor.process_chunks(num_chunks=2)

#         logging.info(f"Generated flashcards: {json.dumps(flashcards, indent=2)}")

#         # Add each flashcard to the Anki deck
#         results = []
#         for card in flashcards:
#             if "front" in card and "back" in card:
#                 result = add_note(deck_name, card["front"], card["back"])
#                 results.append(result)
        
#         return JSONResponse(content=results)
#     except Exception as e:
#         logging.error(f"Error: {e}")
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/autonomous-anki-builder")
async def autonomous_anki_builder(request: Request):
    try:
        req_body = await request.json()
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid JSON")

    input_path = req_body.get('input_path')
    deck_name = req_body.get('deck_name')
    anki_connect_url = req_body.get('anki_connect_url')

    if not input_path or not deck_name or not anki_connect_url:
        raise HTTPException(status_code=400, detail="Please pass 'input_path', 'deck_name', and 'anki_connect_url' in the request body")

    try:
        chunks = process_input(input_path)
        chunk_processor = ChunkProcessor(chunks)
        flashcards = chunk_processor.process_chunks(num_chunks=2)

        logging.info(f"Generated flashcards: {json.dumps(flashcards, indent=2)}")

        # Add each flashcard to the Anki deck
        results = []
        for card in flashcards:
            if "front" in card and "back" in card:
                result = add_note(deck_name, card["front"], card["back"], anki_connect_url)
                if "error" in result:
                    raise HTTPException(status_code=500, detail=result["error"])
                results.append(result)
        
        return JSONResponse(content=results)
    except Exception as e:
        logging.error(f"Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))