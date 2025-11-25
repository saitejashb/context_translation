"""
Unified Translation Engine Interface
Routes to appropriate translation engine based on selection
"""

from glossary import get_glossary

# Import all translation engines
# Always mark IndicTrans2 as available - it will handle errors during translation
HAS_INDICTRANS2 = True
_indictrans2_error_msg = None
try:
    from translation_indictrans2 import translate_with_indictrans2, translate_batch_indictrans2
except ImportError as e:
    _indictrans2_error_msg = str(e)
    print(f"Warning: IndicTrans2 import failed: {e}")
    print("Note: IndicTrans2 will still be attempted during translation.")
    # Create stub functions that will raise errors during translation
    def translate_with_indictrans2(text, glossary=None):
        raise ImportError(f"IndicTrans2 not available: {_indictrans2_error_msg}")
    def translate_batch_indictrans2(sentences, glossary=None):
        raise ImportError(f"IndicTrans2 not available: {_indictrans2_error_msg}")
except Exception as e:
    _indictrans2_error_msg = str(e)
    print(f"Warning: IndicTrans2 import had issues: {e}. Will attempt to use it anyway.")
    # Create stub functions that will raise errors during translation
    def translate_with_indictrans2(text, glossary=None):
        raise Exception(f"IndicTrans2 not available: {_indictrans2_error_msg}")
    def translate_batch_indictrans2(sentences, glossary=None):
        raise Exception(f"IndicTrans2 not available: {_indictrans2_error_msg}")

try:
    from translation_gemini import translate_with_gemini, translate_batch_gemini
    HAS_GEMINI = True
except ImportError:
    HAS_GEMINI = False
    print("Warning: Gemini translation not available")

try:
    from translation_google_standard import translate_google_standard, translate_batch as translate_batch_google_standard
    HAS_GOOGLE_STANDARD = True
except ImportError:
    HAS_GOOGLE_STANDARD = False
    print("Warning: Google Cloud Standard translation not available")

try:
    from translation_google_adaptive import translate_google_adaptive, translate_batch as translate_batch_google_adaptive
    HAS_GOOGLE_ADAPTIVE = True
except ImportError as e:
    HAS_GOOGLE_ADAPTIVE = False
    print(f"Warning: Google Cloud Adaptive translation not available (ImportError: {e})")
    print("  → This usually means 'google-cloud-translate' package is not installed.")
    print("  → Install it with: pip install google-cloud-translate>=3.15.0")
except Exception as e:
    HAS_GOOGLE_ADAPTIVE = False
    print(f"Warning: Google Cloud Adaptive translation not available (Error: {type(e).__name__}: {e})")
    import traceback
    traceback.print_exc()

AVAILABLE_ENGINES = {
    "indictrans2": {
        "name": "IndicTrans2",
        "available": HAS_INDICTRANS2,
        "default": True
    },
    "gemini-3-pro": {
        "name": "Gemini 3 Pro Preview",
        "available": HAS_GEMINI,
        "default": False
    },
    "google-standard": {
        "name": "Google Cloud Translation - Standard",
        "available": HAS_GOOGLE_STANDARD,
        "default": False
    },
    "google-adaptive": {
        "name": "Google Cloud Translation - Adaptive",
        "available": HAS_GOOGLE_ADAPTIVE,
        "default": False
    }
}

def get_available_engines():
    """Get list of available translation engines"""
    return {k: v for k, v in AVAILABLE_ENGINES.items() if v["available"]}

def translate_text(text, engine="indictrans2", glossary=None):
    """
    Translate text using specified engine
    
    Args:
        text: English text to translate
        engine: Engine name ("indictrans2", "gemini-3-pro", "google-standard", "google-adaptive")
        glossary: GlossaryLoader instance (optional)
        
    Returns:
        Translated Telugu text
    """
    if glossary is None:
        glossary = get_glossary()
    
    engine = engine.lower()
    
    if engine == "indictrans2":
        if not HAS_INDICTRANS2:
            raise ValueError("IndicTrans2 engine not available")
        return translate_with_indictrans2(text, glossary)
    
    elif engine == "gemini-3-pro":
        if not HAS_GEMINI:
            raise ValueError("Gemini 3 Pro engine not available")
        return translate_with_gemini(text, glossary)
    
    elif engine == "google-standard":
        if not HAS_GOOGLE_STANDARD:
            raise ValueError("Google Cloud Standard engine not available")
        return translate_google_standard(text, glossary)
    
    elif engine == "google-adaptive":
        if not HAS_GOOGLE_ADAPTIVE:
            raise ValueError("Google Cloud Adaptive engine not available")
        return translate_google_adaptive(text, glossary)
    
    else:
        raise ValueError(f"Unknown translation engine: {engine}")

def translate_batch(sentences, engine="indictrans2", glossary=None):
    """
    Translate batch of sentences using specified engine
    
    Args:
        sentences: List of English sentences
        engine: Engine name
        glossary: GlossaryLoader instance (optional)
        
    Returns:
        List of translated Telugu sentences
    """
    if glossary is None:
        glossary = get_glossary()
    
    engine = engine.lower()
    
    if engine == "indictrans2":
        if not HAS_INDICTRANS2:
            raise ValueError("IndicTrans2 engine not available")
        return translate_batch_indictrans2(sentences, glossary)
    
    elif engine == "gemini-3-pro":
        if not HAS_GEMINI:
            raise ValueError("Gemini 3 Pro engine not available")
        return translate_batch_gemini(sentences, glossary)
    
    elif engine == "google-standard":
        if not HAS_GOOGLE_STANDARD:
            raise ValueError("Google Cloud Standard engine not available")
        return translate_batch_google_standard(sentences, glossary)
    
    elif engine == "google-adaptive":
        if not HAS_GOOGLE_ADAPTIVE:
            raise ValueError("Google Cloud Adaptive engine not available")
        return translate_batch_google_adaptive(sentences, glossary)
    
    else:
        raise ValueError(f"Unknown translation engine: {engine}")

