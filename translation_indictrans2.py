"""
IndicTrans2 Translation Engine (Local Inference)
Uses IndicTrans2 model directly for high-fidelity Indian-language translations
"""

import os
from dotenv import load_dotenv
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit.processor import IndicProcessor
from glossary import apply_glossary, get_glossary
import threading

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

# Thread lock for model access (PyTorch models need thread-safe access)
_model_lock = threading.Lock()

# Language mappings
LANGUAGES = {
    "Assamese": "asm_Beng",
    "Bengali": "ben_Beng",
    "Bodo": "brx_Deva",
    "Dogri": "doi_Deva",
    "English": "eng_Latn",
    "Gujarati": "guj_Gujr",
    "Hindi": "hin_Deva",
    "Kannada": "kan_Knda",
    "Kashmiri (Arabic)": "kas_Arab",
    "Kashmiri (Devanagari)": "kas_Deva",
    "Konkani": "gom_Deva",
    "Maithili": "mai_Deva",
    "Malayalam": "mal_Mlym",
    "Manipuri (Bengali)": "mni_Beng",
    "Manipuri (Meitei)": "mni_Mtei",
    "Marathi": "mar_Deva",
    "Nepali": "npi_Deva",
    "Odia": "ory_Orya",
    "Punjabi": "pan_Guru",
    "Sanskrit": "san_Deva",
    "Santali": "sat_Olck",
    "Sindhi (Arabic)": "snd_Arab",
    "Sindhi (Devanagari)": "snd_Deva",
    "Tamil": "tam_Taml",
    "Telugu": "tel_Telu",
    "Urdu": "urd_Arab"
}

def get_language_code(lang):
    """
    Returns the language code for a given language name.
    If the input is already a valid code, returns it.
    Returns None if not found.
    """
    if lang in LANGUAGES:
        return LANGUAGES[lang]
    
    if lang in LANGUAGES.values():
        return lang
        
    return None

def print_supported_languages():
    print("Supported Languages:")
    for lang, code in LANGUAGES.items():
        print(f"{lang}: {code}")

class IndicTrans2Translator:
    """IndicTrans2 Translation Engine (Local Inference)"""
    
    def __init__(self, model_name="ai4bharat/indictrans2-en-indic-1B", device=None, src_lang="en", target_lang="te"):
        """
        Initialize IndicTrans2 translator
        
        Args:
            model_name: HuggingFace model name (default: "ai4bharat/indictrans2-en-indic-1B")
            device: Device to use ("cuda", "cpu", or None for auto-detect)
            src_lang: Source language code (default: "en")
            target_lang: Target language code (default: "te" for Telugu)
        """
        # Ensure model_name is never None
        self.model_name = model_name if model_name is not None else "ai4bharat/indictrans2-en-indic-1B"
        
        # Device selection: prioritize GPU if available
        if device is not None:
            self.device = device
        elif torch.cuda.is_available():
            self.device = "cuda"
            print(f"[IndicTrans2] CUDA available - will use GPU: {torch.cuda.get_device_name(0)}")
            print(f"[IndicTrans2] GPU Memory: {torch.cuda.get_device_properties(0).total_memory / 1024**3:.2f} GB")
        else:
            self.device = "cpu"
            print(f"[IndicTrans2] WARNING: CUDA not available - will use CPU (slower)")
        
        self.src_lang = src_lang
        self.target_lang = target_lang
        self._model = None
        self._tokenizer = None
        self._processor = None
        self._initialized = False
        
    def _initialize(self):
        """Lazy initialization of the model - thread-safe"""
        if self._initialized:
            return
        
        # Use lock to ensure only one thread initializes the model
        with _model_lock:
            # Double-check after acquiring lock (another thread might have initialized)
            if self._initialized:
                return
            
            try:
                print(f"[IndicTrans2] Loading model {self.model_name} on {self.device}...")
                
                self._tokenizer = AutoTokenizer.from_pretrained(
                    self.model_name, 
                    trust_remote_code=True, 
                    token=HF_TOKEN
                )
                
                # Determine torch_dtype and attn_implementation based on device
                torch_dtype = torch.float16 if "cuda" in self.device else torch.float32
                attn_implementation = "flash_attention_2" if "cuda" in self.device else "eager"
                
                try:
                    self._model = AutoModelForSeq2SeqLM.from_pretrained(
                        self.model_name, 
                        trust_remote_code=True, 
                        torch_dtype=torch_dtype, 
                        attn_implementation=attn_implementation,
                        token=HF_TOKEN
                    ).to(self.device)
                except Exception as e:
                    print(f"[IndicTrans2] Failed to load with {attn_implementation}, falling back to eager execution. Error: {e}")
                    self._model = AutoModelForSeq2SeqLM.from_pretrained(
                        self.model_name, 
                        trust_remote_code=True, 
                        torch_dtype=torch_dtype, 
                        attn_implementation="eager",
                        token=HF_TOKEN
                    ).to(self.device)
                    
                self._processor = IndicProcessor(inference=True)
                self._model.eval()
                
                # Set CUDA device explicitly if using GPU
                if self.device == "cuda":
                    torch.cuda.set_device(0)
                    # Ensure model is on the correct CUDA device
                    self._model = self._model.cuda()
                
                self._initialized = True
                
                # Extensive verification for GPU (RTX 5090)
                if self.device == "cuda":
                    # Check that model parameters are actually on GPU
                    next_param = next(self._model.parameters())
                    actual_device = str(next_param.device)
                    if "cuda" not in actual_device:
                        raise Exception(f"CRITICAL: Model was supposed to load on GPU but is on {actual_device}")
                    
                    # Verify GPU name
                    gpu_name = torch.cuda.get_device_name(0)
                    print(f"[IndicTrans2] Model loaded on GPU: {gpu_name}")
                    print(f"[IndicTrans2] Model device verified: {actual_device}")
                    
                    # Verify GPU memory usage
                    torch.cuda.synchronize()
                    memory_allocated = torch.cuda.memory_allocated(0) / 1024**3
                    memory_reserved = torch.cuda.memory_reserved(0) / 1024**3
                    print(f"[IndicTrans2] GPU Memory Allocated: {memory_allocated:.2f} GB")
                    print(f"[IndicTrans2] GPU Memory Reserved: {memory_reserved:.2f} GB")
                    
                    if memory_allocated < 0.1:
                        raise Exception(f"CRITICAL: GPU memory allocated ({memory_allocated:.2f} GB) is suspiciously low. Model may not be properly loaded.")
                    
                    # Verify RTX 5090 specifically
                    if "5090" in gpu_name.upper() or "RTX 5090" in gpu_name.upper():
                        print(f"[IndicTrans2] ✓ Confirmed: RTX 5090 detected and model loaded successfully")
                    else:
                        print(f"[IndicTrans2] ⚠ WARNING: Expected RTX 5090 but found: {gpu_name}")
                else:
                    print(f"[IndicTrans2] Model loaded successfully on CPU")
                
            except Exception as e:
                print(f"[IndicTrans2] Error initializing model: {str(e)}")
                import traceback
                print(traceback.format_exc())
                raise
    
    def translate(self, text, glossary=None, src_lang="English", tgt_lang="Telugu", max_length=512, num_beams=5):
        """
        Translate text using IndicTrans2 model
        
        Args:
            text: English text to translate
            glossary: GlossaryLoader instance (optional)
            src_lang: Source language name (default: "English")
            tgt_lang: Target language name (default: "Telugu")
            max_length: Maximum generation length (default: 512)
            num_beams: Number of beams for beam search (default: 5)
            
        Returns:
            Translated text
        """
        if not text or not text.strip():
            return text
        
        if glossary is None:
            glossary = get_glossary()
        
        try:
            # Initialize model if not already done
            print(f"[IndicTrans2] translate() called - initializing model if needed...")
            self._initialize()
            
            if not self._initialized:
                raise Exception("Model initialization failed - _initialized is False")
            
            if self._model is None:
                raise Exception("Model is None after initialization")
            
            print(f"[IndicTrans2] Model ready. Device: {self.device}, Model on: {next(self._model.parameters()).device}")
            print(f"[IndicTrans2] Translating text (length: {len(text)}) from {src_lang} to {tgt_lang}")
            
            # Get language codes
            src_code = get_language_code(src_lang)
            tgt_code = get_language_code(tgt_lang)
            
            if not src_code:
                print(f"[IndicTrans2] Error: Unsupported source language '{src_lang}'")
                print_supported_languages()
                return apply_glossary(text, glossary, strict_mode=True)
            
            if not tgt_code:
                print(f"[IndicTrans2] Error: Unsupported target language '{tgt_lang}'")
                print_supported_languages()
                return apply_glossary(text, glossary, strict_mode=True)
            
            # Convert text to list if needed
            if isinstance(text, str):
                input_sentences = [text]
            else:
                input_sentences = text
            
            # Preprocess
            batch = self._processor.preprocess_batch(
                input_sentences,
                src_lang=src_code,
                tgt_lang=tgt_code,
            )
            
            # Tokenize
            inputs = self._tokenizer(
                batch,
                truncation=True,
                padding="longest",
                return_tensors="pt",
                return_attention_mask=True,
            ).to(self.device)
            
            # Generate translation - use lock for thread safety
            print(f"[IndicTrans2] Starting model.generate() on {self.device}...")
            print(f"[IndicTrans2] Input shape: {inputs['input_ids'].shape}, Device: {inputs['input_ids'].device}")
            print(f"[IndicTrans2] Acquiring model lock for thread-safe inference...")
            with _model_lock:
                print(f"[IndicTrans2] Model lock acquired, running inference...")
                with torch.no_grad():
                    generated_tokens = self._model.generate(
                        **inputs,
                        use_cache=False,
                        min_length=0,
                        max_length=max_length,
                        num_beams=num_beams,
                        num_return_sequences=1,
                    )
                print(f"[IndicTrans2] Model.generate() completed. Output shape: {generated_tokens.shape}")
            print(f"[IndicTrans2] Model lock released")
            
            # Decode
            generated_tokens = self._tokenizer.batch_decode(
                generated_tokens,
                skip_special_tokens=True,
                clean_up_tokenization_spaces=True,
            )
            
            # Postprocess
            translations = self._processor.postprocess_batch(generated_tokens, lang=tgt_code)
            
            # Get first translation (or join if multiple)
            if isinstance(translations, list) and len(translations) > 0:
                translated = translations[0]
            else:
                translated = text
            
            # Apply glossary AFTER translation to enforce terminology
            if translated and translated != text:
                for _ in range(3):
                    translated = apply_glossary(translated, glossary, strict_mode=True)
            
            return translated
            
        except Exception as e:
            print(f"[IndicTrans2] Translation error: {str(e)}")
            import traceback
            traceback.print_exc()
            # Re-raise the exception so it can be caught by the caller
            # Don't silently return original text - let the caller handle the error
            raise
    
    def translate_batch(self, sentences, glossary=None, src_lang="English", tgt_lang="Telugu", max_length=512, num_beams=5):
        """
        Translate a batch of sentences using IndicTrans2 model
        Translates each sentence individually to ensure proper results
        
        Args:
            sentences: List of English sentences
            glossary: GlossaryLoader instance (optional)
            src_lang: Source language name (default: "English")
            tgt_lang: Target language name (default: "Telugu")
            max_length: Maximum generation length (default: 512)
            num_beams: Number of beams for beam search (default: 5)
            
        Returns:
            List of translated sentences
        """
        if glossary is None:
            glossary = get_glossary()
        
        if not sentences or all(not s.strip() for s in sentences):
            return [""] * len(sentences) if sentences else []
        
        # Initialize model if not already done
        print(f"[IndicTrans2] translate_batch() called with {len(sentences)} sentences")
        try:
            print(f"[IndicTrans2] Initializing model for batch translation...")
            self._initialize()
            
            if not self._initialized:
                raise Exception("Model initialization failed - _initialized is False")
            
            if self._model is None:
                raise Exception("Model is None after initialization")
            
            print(f"[IndicTrans2] Model ready for batch. Device: {self.device}, Model on: {next(self._model.parameters()).device}")
        except Exception as e:
            print(f"[IndicTrans2] Failed to initialize model: {str(e)}")
            import traceback
            traceback.print_exc()
            # Return original sentences with glossary applied on error
            return [apply_glossary(sentence, glossary, strict_mode=True) for sentence in sentences]
        
        # Translate each sentence individually
        translated_sentences = []
        
        print(f"[IndicTrans2] Translating batch: {len(sentences)} sentences individually...")
        
        for i, sentence in enumerate(sentences):
            if not sentence or not sentence.strip():
                translated_sentences.append("")
                continue
            
            try:
                print(f"[IndicTrans2] Translating sentence {i+1}/{len(sentences)} (length: {len(sentence)})")
                
                # Use translate method for each sentence
                translated = self.translate(
                    sentence, 
                    glossary=glossary, 
                    src_lang=src_lang, 
                    tgt_lang=tgt_lang,
                    max_length=max_length,
                    num_beams=num_beams
                )
                
                translated_sentences.append(translated)
                
            except Exception as e:
                print(f"[IndicTrans2] Translation error for sentence {i+1}: {str(e)}")
                import traceback
                traceback.print_exc()
                # Don't silently continue - raise the exception to fail fast
                # This will help identify the issue
                raise Exception(f"Failed to translate sentence {i+1}/{len(sentences)}: {str(e)}") from e
        
        print(f"[IndicTrans2] Batch translation completed: {len(translated_sentences)} sentences")
        return translated_sentences

# Global instance (lazy loaded)
_indictrans2_instance = None

def get_indictrans2_translator(src_lang="en", target_lang="te", model_name=None):
    """Get or create global IndicTrans2 translator instance"""
    global _indictrans2_instance
    if _indictrans2_instance is None:
        # Use default model name if not provided
        if model_name is None:
            model_name = "ai4bharat/indictrans2-en-indic-1B"
        _indictrans2_instance = IndicTrans2Translator(
            model_name=model_name,
            src_lang=src_lang,
            target_lang=target_lang
        )
    return _indictrans2_instance

def translate_with_indictrans2(text, glossary=None, src_lang="en", target_lang="te"):
    """Translate using IndicTrans2 (local inference)"""
    translator = get_indictrans2_translator(src_lang=src_lang, target_lang=target_lang)
    return translator.translate(text, glossary=glossary, src_lang="English", tgt_lang="Telugu")

def translate_batch_indictrans2(sentences, glossary=None, src_lang="en", target_lang="te"):
    """Translate batch using IndicTrans2 (local inference)"""
    translator = get_indictrans2_translator(src_lang=src_lang, target_lang=target_lang)
    return translator.translate_batch(sentences, glossary=glossary, src_lang="English", tgt_lang="Telugu")
