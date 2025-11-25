"""
Shared APIs Module
Handles Synonyms and Transliteration API calls
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API configuration
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-2.5-flash:generateContent"

def get_synonyms(word, lang="telugu"):
    """
    Get synonyms for a word using Gemini API
    
    Args:
        word: Word to find synonyms for
        lang: Language (default: telugu)
        
    Returns:
        List of synonyms
    """
    if not word or not word.strip():
        return []
    
    word = word.strip()
    
    try:
        # Prepare prompt for Gemini
        prompt = f"""Find 5-10 synonyms for the Telugu word "{word}". 
Return only a JSON array of synonyms in Telugu script, no explanations.
Example format: ["synonym1", "synonym2", "synonym3"]
If no synonyms found, return empty array []."""

        # Make API request
        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract text from Gemini response
            if 'candidates' in data and len(data['candidates']) > 0:
                content = data['candidates'][0].get('content', {})
                parts = content.get('parts', [])
                if parts and 'text' in parts[0]:
                    text_response = parts[0]['text'].strip()
                    
                    # Try to parse as JSON
                    try:
                        # Remove markdown code blocks if present
                        text_response = text_response.replace('```json', '').replace('```', '').strip()
                        synonyms = json.loads(text_response)
                        if isinstance(synonyms, list):
                            return synonyms
                    except json.JSONDecodeError:
                        # If not JSON, try to extract words from text
                        import re
                        # Extract words in quotes or Telugu script
                        matches = re.findall(r'["\']([^"\']+)["\']|([\u0C00-\u0C7F]+)', text_response)
                        synonyms = []
                        for match in matches:
                            word_found = match[0] if match[0] else match[1]
                            if word_found and word_found != word:
                                synonyms.append(word_found)
                        return synonyms[:10]  # Limit to 10 synonyms
        
        # If API call failed, return empty list
        if response.status_code != 200:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            print(f"Gemini API error: {response.status_code} - {error_data}")
        return []
        
    except Exception as e:
        print(f"Error getting synonyms: {e}")
        return []

def transliterate_english_to_telugu(text):
    """
    Transliterate English text to Telugu script using Gemini API
    
    Args:
        text: English text to transliterate (phonetic conversion)
        
    Returns:
        Transliterated text in Telugu script
    """
    if not text or not text.strip():
        return text
    
    text = text.strip()
    
    try:
        # Prepare prompt for Gemini
        prompt = f"""Transliterate the following English text to Telugu script phonetically.
Do NOT translate the meaning, only convert the pronunciation to Telugu script.
Preserve the original structure and spacing.

Text to transliterate: "{text}"

Return only the transliterated text in Telugu script, nothing else."""

        # Make API request
        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }]
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            # Extract text from Gemini response
            if 'candidates' in data and len(data['candidates']) > 0:
                content = data['candidates'][0].get('content', {})
                parts = content.get('parts', [])
                if parts and 'text' in parts[0]:
                    transliterated = parts[0]['text'].strip()
                    # Remove any quotes if present
                    transliterated = transliterated.strip('"').strip("'").strip()
                    return transliterated
        
        # If API call failed, return original text
        if response.status_code != 200:
            error_data = response.json() if response.headers.get('content-type', '').startswith('application/json') else {}
            print(f"Gemini API error: {response.status_code} - {error_data}")
        return text
        
    except Exception as e:
        print(f"Transliteration error: {e}")
        return text

