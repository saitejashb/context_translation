"""
Government-Grade Telugu Translation Engine
Powered by Google Gemini 2.5 Flash (via REST API)
Uses glossary.csv via GlossaryLoader for strict terminology enforcement
"""

import os
import re
import requests
import json
import time
from dotenv import load_dotenv
from glossary import GlossaryLoader

# Load environment variables from .env file
load_dotenv()

# -------------------------------
# Gemini API Setup (REST API)
# -------------------------------
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is required. Please set it in your .env file.")
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent"

# Rate limiting - track requests per minute
_last_request_time = {}

# Separator for batch translation (must be unique and unlikely to appear in text)
# Using a very unique pattern with numbers and special chars that won't be translated
SEPARATOR = "___SEGMENT_BREAK_XYZ789___"

# -------------------------------
# Output Cleaner
# -------------------------------
def clean_telugu_output(text):
    """Clean output to ensure pure Telugu"""
    if not text:
        return ""
    
    # Strip quotes + trim
    text = text.strip().strip('"').strip("'").strip()
    
    # Remove known unwanted English phrases
    BLOCKLIST = [
        "Please provide", "You have indicated",
        "appears to be", "Here is", "Translation",
        "Note:", "NOTE:", "Important:", "As an AI", 
        "Text to translate", "Source text"
    ]
    
    for bad in BLOCKLIST:
        text = text.replace(bad, "")
    
    # Remove placeholder artifacts
    text = re.sub(r'[@#\-\*=]{2,}', "", text)
    
    # Collapse excessive spacing
    text = re.sub(r"\s+", " ", text).strip()
    
    return text

# -------------------------------
# Main Translator
# -------------------------------
def translate_with_gemini(text, glossary=None, enforce_glossary=True):
    """Translate English → Government-Grade Telugu"""
    
    if not text or not text.strip():
        return text
    
    if not GEMINI_API_KEY:
        return f"GEMINI_API_KEY not set. Original: {text}"
    
    if glossary is None:
        glossary = GlossaryLoader()
    
    # Prepare glossary section
    glossary_entries = "\n".join(
        [f'"{eng}" → "{tel}"' for eng, tel in list(glossary.glossary.items())[:500]]
    )
    
    # Check if text contains separator markers (batched text)
    has_separators = SEPARATOR in text
    
    # Professional system prompt
    structure_note = ""
    if has_separators:
        structure_note = f"\n\nCRITICAL STRUCTURE PRESERVATION:\nThe text contains '{SEPARATOR}' markers. These are STRUCTURE MARKERS, NOT content.\n- DO NOT translate these markers\n- DO NOT change these markers\n- DO NOT remove these markers\n- DO NOT modify these markers in any way\n- Keep them EXACTLY as '{SEPARATOR}'\n- Translate only the text BETWEEN the markers\n- Each segment between markers should be translated separately\n- The markers must appear in your output EXACTLY as shown above"
    
    prompt = f"""You are an expert Telugu translator specializing in official government documents and legal texts. Your translations must be accurate, formal, and maintain the exact structure of the original document.

CRITICAL TRANSLATION RULES (MUST FOLLOW):

1. **GLOSSARY TERMS ARE MANDATORY**: When you see any English term from the glossary below, you MUST use the EXACT Telugu translation provided. Do NOT translate glossary terms differently.

2. **PRESERVE STRUCTURE COMPLETELY**: 
   - Keep all line breaks, paragraphs, and spacing exactly as in the original
   - Preserve all numbers, dates, codes, and abbreviations exactly (e.g., "G.O.Rt.No.239" stays as "G.O.Rt.No.239")
   - Keep all punctuation marks, special characters, and formatting

3. **FORMAL GOVERNMENT LANGUAGE**: Use formal, official Telugu suitable for government orders, circulars, and official communications. Avoid colloquial or informal language.

4. **ACCURACY FIRST**: Translate with maximum accuracy. Every word matters in government documents.

5. **NO ADDITIONS**: Do not add explanations, notes, or commentary. Only provide the Telugu translation.

6. **CONTEXT AWARENESS**: Understand the context and translate accordingly, but always prioritize glossary terms when they appear.{structure_note}

MANDATORY GLOSSARY (Use these EXACT translations):
{glossary_entries}

Now translate the following English text to Telugu following all rules above:

{text}

Telugu Translation:"""
    
    # Send to Gemini using REST API
    try:
        # Rate limiting - minimal delay (0.5 seconds) for faster processing
        current_time = time.time()
        model_name = "gemini-2.5-flash"
        if model_name in _last_request_time:
            time_since_last = current_time - _last_request_time[model_name]
            if time_since_last < 0.5:  # Minimal delay - 0.5 seconds between requests
                wait_time = 0.5 - time_since_last
                time.sleep(wait_time)
        
        url = f"{GEMINI_API_URL}?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [{
                "parts": [{
                    "text": prompt
                }]
            }],
            "generationConfig": {
                "temperature": 0.0,  # Lower temperature for more consistent, accurate translations
                "topK": 1,  # More deterministic output
                "topP": 0.95,
                "maxOutputTokens": 8192
            }
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=60)
        
        if response.status_code == 200:
            data = response.json()
            
            if 'candidates' in data and len(data['candidates']) > 0:
                candidate = data['candidates'][0]
                content = candidate.get('content', {})
                parts = content.get('parts', [])
                    
                if parts and len(parts) > 0:
                    # Try different ways to get the text
                    if 'text' in parts[0]:
                        translated = parts[0]['text'].strip()
                    elif isinstance(parts[0], str):
                        translated = parts[0].strip()
                    else:
                        # Try to get text from the part directly
                        translated = str(parts[0]).strip()
                        print(f"WARNING: Using string conversion for parts[0]: {translated[:100]}")
                    
                    if translated:
                        _last_request_time[model_name] = time.time()
                        
                        # Check if we got a valid translation (should contain Telugu characters)
                        has_telugu = any("\u0C00" <= ch <= "\u0C7F" for ch in translated)
                        if not has_telugu and len(translated) > 50:
                            print(f"[Gemini] ERROR: Gemini returned English instead of Telugu!")
                            print(f"[Gemini] Response preview: {translated[:500]}")
                            print(f"[Gemini] Full response structure: {json.dumps(data, indent=2)[:1000]}")
                            # Try to extract translation if it's buried in the response
                            if 'Telugu Translation:' in translated:
                                # Try to extract after "Telugu Translation:"
                                parts = translated.split('Telugu Translation:', 1)
                                if len(parts) > 1:
                                    extracted = parts[1].strip()
                                    # Remove any leading/trailing quotes or markers
                                    extracted = extracted.strip('"').strip("'").strip()
                                    if any("\u0C00" <= ch <= "\u0C7F" for ch in extracted) and len(extracted) > 10:
                                        print(f"[Gemini] Found translation after extraction (length: {len(extracted)} chars)")
                                        translated = extracted
                                    else:
                                        print(f"[Gemini] ERROR: Still no Telugu after extraction")
                                        raise Exception("Gemini returned English instead of Telugu translation")
                                else:
                                    raise Exception("Gemini returned English instead of Telugu translation")
                            elif 'translation' in translated.lower() and len(translated) > 200:
                                # Might be a response explaining why it can't translate
                                print(f"[Gemini] Response seems to be an explanation, not a translation")
                                raise Exception("Gemini returned explanation instead of translation")
                            else:
                                # Check if it's just the original text
                                if translated.strip() == text.strip()[:len(translated.strip())]:
                                    raise Exception("Gemini returned original text instead of translation")
                                else:
                                    raise Exception("Gemini returned English text instead of Telugu translation")
                        
                        # Remove any accidental separator-like text that might have been translated
                        # Clean up any variations of the separator that might appear
                        # But preserve the actual separator if it exists
                        
                        # Clean the output (but preserve separators if present)
                        if SEPARATOR not in translated:
                            translated = clean_telugu_output(translated)
                        else:
                            # If separators are present, clean each segment separately
                            segments = translated.split(SEPARATOR)
                            cleaned_segments = [clean_telugu_output(seg) for seg in segments]
                            translated = SEPARATOR.join(cleaned_segments)
                        
                        # Apply glossary multiple times to enforce terminology (more aggressive)
                        from glossary import apply_glossary
                        for _ in range(5):  # Increased from 3 to 5 for better glossary enforcement
                            translated = apply_glossary(translated, glossary, strict_mode=True)
                        
                        return translated
                    else:
                        # Empty text - might be blocked or filtered
                        finish_reason = candidate.get('finishReason', 'UNKNOWN')
                        print(f"[Gemini] ERROR: Empty translation response, finish reason: {finish_reason}")
                        print(f"[Gemini] Full response: {json.dumps(data, indent=2)[:1000]}")
                        if finish_reason == 'SAFETY':
                            raise Exception("Gemini response blocked by safety filters")
                        elif finish_reason == 'RECITATION':
                            raise Exception("Gemini response blocked due to recitation policy")
                        else:
                            raise Exception(f"Gemini returned empty response, finish reason: {finish_reason}")
                else:
                    # No parts - check finish reason
                    finish_reason = candidate.get('finishReason', 'UNKNOWN')
                    print(f"[Gemini] ERROR: No parts in response, finish reason: {finish_reason}")
                    print(f"[Gemini] Full response: {json.dumps(data, indent=2)[:1000]}")
                    if finish_reason == 'SAFETY':
                        raise Exception("Gemini response blocked by safety filters")
                    elif finish_reason == 'RECITATION':
                        raise Exception("Gemini response blocked due to recitation policy")
                    else:
                        raise Exception(f"Gemini returned no parts, finish reason: {finish_reason}")
            else:
                print(f"[Gemini] ERROR: No candidates in response")
                print(f"[Gemini] Full response: {json.dumps(data, indent=2)[:1000]}")
                raise Exception("Gemini API returned no candidates in response")
        else:
            error_text = response.text[:1000] if hasattr(response, 'text') else str(response)
            print(f"[Gemini] ERROR: API returned status {response.status_code}")
            print(f"[Gemini] Error response: {error_text}")
            try:
                error_data = response.json()
                print(f"[Gemini] Error JSON: {json.dumps(error_data, indent=2)}")
            except:
                pass
            raise Exception(f"Gemini API error: {response.status_code} - {error_text[:200]}")
            
    except Exception as e:
        print(f"[Gemini] CRITICAL: Translation error: {e}")
        import traceback
        print(traceback.format_exc())
        # Don't return original text silently - raise error so caller knows
        raise Exception(f"Gemini translation failed: {str(e)}")

# -------------------------------
# Batch Translator
# -------------------------------
def translate_batch_gemini(sentences, glossary=None):
    """
    Translate batch of sentences - OPTIMIZED: Batch in chunks to balance speed and structure preservation
    """
    if glossary is None:
        glossary = GlossaryLoader()
    
    if not sentences or all(not s.strip() for s in sentences):
        return [""] * len(sentences)
    
    # Batch sentences in larger chunks for maximum speed
    # This is much faster than sentence-by-sentence but still preserves structure
    chunk_size = 15  # Process 15 sentences at a time for faster translation
    translations = []
    
    for chunk_start in range(0, len(sentences), chunk_size):
        chunk = sentences[chunk_start:chunk_start + chunk_size]
        
        # Join chunk with separator
        chunk_text = SEPARATOR.join(chunk)
        
        try:
            # Translate the chunk
            translated_chunk = translate_with_gemini(chunk_text, glossary)
            
            # Split back by separator
            # Clean up any corrupted separator patterns
            translated_chunk = re.sub(r'\|{3,}', SEPARATOR, translated_chunk)
            translated_chunk = translated_chunk.replace("|||SEGMENT|||", SEPARATOR)
            translated_chunk = translated_chunk.replace("||||||", SEPARATOR)
            
            chunk_translations = translated_chunk.split(SEPARATOR)
            
            # Ensure we have the right number of translations
            while len(chunk_translations) < len(chunk):
                chunk_translations.append("")
            
            translations.extend(chunk_translations[:len(chunk)])
            
        except Exception as e:
            error_msg = str(e)
            print(f"[Gemini] ERROR translating chunk {chunk_start//chunk_size + 1}: {error_msg}")
            import traceback
            print(traceback.format_exc())
            
            # Check if it's an API key error - provide helpful message and continue with original text
            if "403" in error_msg or "PERMISSION_DENIED" in error_msg or "API key" in error_msg.lower() or "leaked" in error_msg.lower():
                print(f"[Gemini] WARNING: API key issue detected. Please update GEMINI_API_KEY in .env file")
                print(f"[Gemini] Returning original text for this chunk so other engines can continue")
                # Return original sentences for this chunk so other engines can still work
                translations.extend(chunk)
            else:
                # For other errors, raise exception
                raise Exception(f"Gemini batch translation failed at chunk {chunk_start//chunk_size + 1}: {error_msg}")
        
        # Progress indicator
        if (chunk_start + chunk_size) % 20 == 0 or chunk_start + chunk_size >= len(sentences):
            print(f"Translated {min(chunk_start + chunk_size, len(sentences))}/{len(sentences)} segments...")
    
    return translations