"""
IndicTrans2 Translation Engine (API-based)
Uses remote IndicTrans2 API endpoint for high-fidelity Indian-language translations
"""

import requests
import json
from glossary import apply_glossary, get_glossary

# IndicTrans2 API configuration
# Use environment variable if set, otherwise fallback to docker service name
import os
INDICTRANS2_BASE_URL = os.getenv("INDICTRANS2_BASE_URL", "http://indictrans2-nginx:80")
INDICTRANS2_API_URL = f"{INDICTRANS2_BASE_URL}/translate"
INDICTRANS2_LANGUAGES_URL = f"{INDICTRANS2_BASE_URL}/languages"

# Cache for language mappings
_language_mappings = None

def _get_language_mappings():
    """Get language mappings from API and cache them"""
    global _language_mappings
    if _language_mappings is not None:
        return _language_mappings
    
    try:
        response = requests.get(INDICTRANS2_LANGUAGES_URL, timeout=10)
        if response.status_code == 200:
            _language_mappings = response.json()
            print(f"[IndicTrans2] Language mappings loaded: {len(_language_mappings)} languages")
            return _language_mappings
        else:
            print(f"[IndicTrans2] Warning: Could not load language mappings: {response.status_code}")
            return {}
    except Exception as e:
        print(f"[IndicTrans2] Warning: Error loading language mappings: {e}")
        return {}

class IndicTrans2Translator:
    """IndicTrans2 Translation Engine (API-based)"""
    
    def __init__(self, model_name=None, src_lang="en", target_lang="te"):
        """
        Initialize IndicTrans2 translator
        
        Args:
            model_name: Not used (kept for compatibility)
            src_lang: Source language code (default: "en")
            target_lang: Target language code (default: "te" for Telugu)
        """
        self.src_lang = src_lang
        self.target_lang = target_lang
        self._initialized = True  # API-based, no initialization needed
        print(f"[IndicTrans2] Translator initialized (API-based)")
    
    def _initialize(self):
        """No-op for API-based translator"""
        pass
    
    def translate(self, text, glossary=None):
        """
        Translate text using IndicTrans2 API
        Uses the working translation approach that handles long documents well
        
        Args:
            text: English text to translate
            glossary: GlossaryLoader instance (optional)
            
        Returns:
            Translated Telugu text
        """
        if not text or not text.strip():
            return text
        
        if glossary is None:
            glossary = get_glossary()
        
        try:
            print(f"[IndicTrans2] Translating text (length: {len(text)}) from English to Telugu")
            
            response = requests.post(
                INDICTRANS2_API_URL,
                json={
                    "text": text,
                    "src_lang": "English",
                    "tgt_lang": "Telugu"
                },
                timeout=60,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            result = response.json()
            print(f"[IndicTrans2] API Response received")
            
            # Handle different response formats
            translated = None
            if "translations" in result:
                # API returns {'translations': ['translated text']}
                translations = result["translations"]
                if isinstance(translations, list) and len(translations) > 0:
                    translated = translations[0]
                else:
                    translated = text
            elif "translated_text" in result:
                translated = result["translated_text"]
            elif "translation" in result:
                translated = result["translation"]
            elif "text" in result:
                translated = result["text"]
            else:
                # Fallback: return original text if format is unexpected
                print(f"[IndicTrans2] Unexpected API response format: {result}")
                translated = text
            
            # Apply glossary AFTER translation to enforce terminology
            if translated and translated != text:
                for _ in range(3):
                    translated = apply_glossary(translated, glossary, strict_mode=True)
            
            return translated
            
        except requests.exceptions.Timeout:
            print(f"[IndicTrans2] Translation timeout for text: {text[:50]}...")
            return apply_glossary(text, glossary, strict_mode=True)
        except requests.exceptions.RequestException as e:
            print(f"[IndicTrans2] Translation request error: {str(e)}")
            print(f"[IndicTrans2] Response: {e.response.text if hasattr(e, 'response') and e.response else 'No response'}")
            return apply_glossary(text, glossary, strict_mode=True)
        except Exception as e:
            print(f"[IndicTrans2] Translation error: {str(e)}")
            import traceback
            print(traceback.format_exc())
            return apply_glossary(text, glossary, strict_mode=True)
    
    def translate_batch(self, sentences, glossary=None):
        """
        Translate a batch of sentences using IndicTrans2 API
        Translates each sentence individually (like the working code) to ensure proper results
        
        Args:
            sentences: List of English sentences
            glossary: GlossaryLoader instance (optional)
            
        Returns:
            List of translated Telugu sentences
        """
        if glossary is None:
            glossary = get_glossary()
        
        if not sentences or all(not s.strip() for s in sentences):
            return [""] * len(sentences) if sentences else []
        
        # Translate each sentence individually (like the working code)
        # This ensures each paragraph gets properly translated
        translated_sentences = []
        
        print(f"[IndicTrans2] Translating batch: {len(sentences)} sentences individually...")
        
        for i, sentence in enumerate(sentences):
            if not sentence or not sentence.strip():
                translated_sentences.append("")
                continue
            
            try:
                print(f"[IndicTrans2] Translating sentence {i+1}/{len(sentences)} (length: {len(sentence)})")
                
                response = requests.post(
                    INDICTRANS2_API_URL,
                    json={
                        "text": sentence,
                        "src_lang": "English",
                        "tgt_lang": "Telugu"
                    },
                    timeout=60,
                    headers={'Content-Type': 'application/json'}
                )
                
                response.raise_for_status()
                result = response.json()
                
                # Handle different response formats
                translated = None
                if "translations" in result:
                    # API returns {'translations': ['translated text']}
                    translations = result["translations"]
                    if isinstance(translations, list) and len(translations) > 0:
                        translated = translations[0]
                    else:
                        translated = sentence
                elif "translated_text" in result:
                    translated = result["translated_text"]
                elif "translation" in result:
                    translated = result["translation"]
                elif "text" in result:
                    translated = result["text"]
                else:
                    # Fallback: return original text if format is unexpected
                    print(f"[IndicTrans2] Unexpected API response format: {result}")
                    translated = sentence
                
                # Apply glossary AFTER translation to enforce terminology
                if translated and translated != sentence:
                    for _ in range(3):
                        translated = apply_glossary(translated, glossary, strict_mode=True)
                
                translated_sentences.append(translated)
                
            except requests.exceptions.Timeout:
                print(f"[IndicTrans2] Translation timeout for sentence {i+1}")
                translated_sentences.append(apply_glossary(sentence, glossary, strict_mode=True))
            except requests.exceptions.RequestException as e:
                print(f"[IndicTrans2] Translation request error for sentence {i+1}: {str(e)}")
                print(f"[IndicTrans2] Response: {e.response.text if hasattr(e, 'response') and e.response else 'No response'}")
                translated_sentences.append(apply_glossary(sentence, glossary, strict_mode=True))
            except Exception as e:
                print(f"[IndicTrans2] Translation error for sentence {i+1}: {str(e)}")
                import traceback
                print(traceback.format_exc())
                translated_sentences.append(apply_glossary(sentence, glossary, strict_mode=True))
        
        print(f"[IndicTrans2] Batch translation completed: {len(translated_sentences)} sentences")
        return translated_sentences

# Global instance
_indictrans2_instance = None

def get_indictrans2_translator(src_lang="en", target_lang="te", model_name=None):
    """Get or create global IndicTrans2 translator instance"""
    global _indictrans2_instance
    if _indictrans2_instance is None:
        _indictrans2_instance = IndicTrans2Translator(
            model_name=model_name,
            src_lang=src_lang,
            target_lang=target_lang
        )
    return _indictrans2_instance

def translate_with_indictrans2(text, glossary=None, src_lang="en", target_lang="te"):
    """Translate using IndicTrans2 API"""
    translator = get_indictrans2_translator(src_lang=src_lang, target_lang=target_lang)
    return translator.translate(text, glossary=glossary)

def translate_batch_indictrans2(sentences, glossary=None, src_lang="en", target_lang="te"):
    """Translate batch using IndicTrans2 API"""
    translator = get_indictrans2_translator(src_lang=src_lang, target_lang=target_lang)
    return translator.translate_batch(sentences, glossary=glossary)
