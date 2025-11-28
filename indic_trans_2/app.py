from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Union, Optional
from inference import IndicTrans2Translator
from languages import LANGUAGES, get_language_code
import contextlib

# Global translator instance
translator = None

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    global translator
    print("Initializing model...")
    translator = IndicTrans2Translator()
    print("Model initialized.")
    yield
    print("Shutting down...")

app = FastAPI(title="IndicTrans2 API", lifespan=lifespan)

class TranslationRequest(BaseModel):
    text: Union[str, List[str]]
    src_lang: str
    tgt_lang: str
    max_length: Optional[int] = 512
    num_beams: Optional[int] = 5
    num_return_sequences: Optional[int] = 1

@app.get("/languages")
def get_supported_languages():
    return LANGUAGES

@app.post("/translate")
def translate_text(request: TranslationRequest):
    if not translator:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    # Validate languages
    if not get_language_code(request.src_lang):
         raise HTTPException(status_code=400, detail=f"Unsupported source language: {request.src_lang}. Check /languages for supported list.")
    if not get_language_code(request.tgt_lang):
         raise HTTPException(status_code=400, detail=f"Unsupported target language: {request.tgt_lang}. Check /languages for supported list.")

    try:
        translations = translator.translate(
            request.text,
            request.src_lang,
            request.tgt_lang,
            max_length=request.max_length,
            num_beams=request.num_beams,
            num_return_sequences=request.num_return_sequences
        )
        return {"translations": translations}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
