"""
Google Cloud Translation - Standard Translation Engine
Uses REST API with API key
"""

import os
import requests
import json
from dotenv import load_dotenv
from glossary import apply_glossary, get_glossary

# Load environment variables from .env file
load_dotenv()

# Google Cloud Translation API configuration
GOOGLE_TRANSLATE_API_KEY = os.getenv("GOOGLE_TRANSLATE_API_KEY")
GOOGLE_TRANSLATE_API_URL = "https://translation.googleapis.com/language/translate/v2"

HAS_GOOGLE_CLOUD = True  # Using REST API, no library needed

def translate_google_standard(text, glossary=None, target_lang='te'):
    """
    Translate text using Google Cloud Translation (Standard) REST API
    
    Args:
        text: English text to translate
        glossary: GlossaryLoader instance (optional)
        target_lang: Target language code (default: 'te' for Telugu)
        
    Returns:
        Translated Telugu text
    """
    if not text or not text.strip():
        return text
    
    if glossary is None:
        glossary = get_glossary()
    
    if not GOOGLE_TRANSLATE_API_KEY:
        print("Google Cloud Translation API key not set, falling back to glossary-only")
        return apply_glossary(text, glossary, strict_mode=True)
    
    try:
        # Step 1: Translate FULL English text first (don't apply glossary before translation)
        # This ensures all English text gets translated
        url = f"{GOOGLE_TRANSLATE_API_URL}?key={GOOGLE_TRANSLATE_API_KEY}"
        
        payload = {
            "q": text,  # Send original English text
            "target": target_lang,
            "source": "en",
            "format": "text"
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if 'data' in data and 'translations' in data['data']:
                translated = data['data']['translations'][0]['translatedText']
                
                # Step 2: Apply glossary AFTER translation to enforce terminology
                # Apply 3 times to catch any missed terms
                for _ in range(3):
                    translated = apply_glossary(translated, glossary, strict_mode=True)
                
                return translated
            else:
                print(f"Google Cloud Translation API response error: {data}")
                return apply_glossary(text, glossary, strict_mode=True)
        else:
            print(f"Google Cloud Translation API error: {response.status_code} - {response.text}")
            return apply_glossary(text, glossary, strict_mode=True)
        
    except Exception as e:
        print(f"Google Cloud Translation error: {e}")
        return apply_glossary(text, glossary, strict_mode=True)

def translate_batch(sentences, glossary=None, target_lang='te'):
    """
    Translate a batch of sentences - OPTIMIZED: Single API call for entire document
    
    Args:
        sentences: List of English sentences
        glossary: GlossaryLoader instance (optional)
        target_lang: Target language code
        
    Returns:
        List of translated Telugu sentences
    """
    if glossary is None:
        glossary = get_glossary()
    
    # OPTIMIZATION: Join all sentences and translate in ONE API call
    # This is MUCH faster than 64 individual API calls!
    if not sentences or all(not s.strip() for s in sentences):
        return [""] * len(sentences)
    
    # Join sentences with newlines to preserve structure
    full_text = "\n".join(sentences)
    
    # Translate entire document in one call
    translated_full = translate_google_standard(full_text, glossary, target_lang)
    
    # Split back into sentences (preserve count)
    # Simple split by newlines - should work since we joined with \n
    translated_sentences = translated_full.split("\n")
    
    # Ensure we have the same number of translations as inputs
    while len(translated_sentences) < len(sentences):
        translated_sentences.append("")
    
    # Trim to match input length
    translated_sentences = translated_sentences[:len(sentences)]
    
    return translated_sentences

