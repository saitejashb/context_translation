import os
from dotenv import load_dotenv
import torch
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer
from IndicTransToolkit.processor import IndicProcessor
from languages import get_language_code, print_supported_languages

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")

class IndicTrans2Translator:
    def __init__(self, model_name="ai4bharat/indictrans2-en-indic-1B", device=None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        print(f"Loading model {model_name} on {self.device}...")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True, token=HF_TOKEN)
        
        # Determine torch_dtype and attn_implementation based on device
        torch_dtype = torch.float16 if "cuda" in self.device else torch.float32
        attn_implementation = "flash_attention_2" if "cuda" in self.device else "eager"
        
        try:
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name, 
                trust_remote_code=True, 
                torch_dtype=torch_dtype, 
                attn_implementation=attn_implementation,
                token=HF_TOKEN
            ).to(self.device)
        except Exception as e:
            print(f"Failed to load with {attn_implementation}, falling back to eager execution. Error: {e}")
            self.model = AutoModelForSeq2SeqLM.from_pretrained(
                model_name, 
                trust_remote_code=True, 
                torch_dtype=torch_dtype, 
                attn_implementation="eager",
                token=HF_TOKEN
            ).to(self.device)
            
        self.ip = IndicProcessor(inference=True)
        self.model.eval()

    def translate(self, input_sentences, src_lang, tgt_lang, max_length=512, num_beams=5, num_return_sequences=1):
        src_code = get_language_code(src_lang)
        tgt_code = get_language_code(tgt_lang)

        if not src_code:
            print(f"Error: Unsupported source language '{src_lang}'")
            print_supported_languages()
            return None
        
        if not tgt_code:
            print(f"Error: Unsupported target language '{tgt_lang}'")
            print_supported_languages()
            return None

        if isinstance(input_sentences, str):
            input_sentences = [input_sentences]

        batch = self.ip.preprocess_batch(
            input_sentences,
            src_lang=src_code,
            tgt_lang=tgt_code,
        )

        inputs = self.tokenizer(
            batch,
            truncation=True,
            padding="longest",
            return_tensors="pt",
            return_attention_mask=True,
        ).to(self.device)

        with torch.no_grad():
            generated_tokens = self.model.generate(
                **inputs,
                use_cache=False,
                min_length=0,
                max_length=max_length,
                num_beams=num_beams,
                num_return_sequences=num_return_sequences,
            )

        generated_tokens = self.tokenizer.batch_decode(
            generated_tokens,
            skip_special_tokens=True,
            clean_up_tokenization_spaces=True,
        )

        translations = self.ip.postprocess_batch(generated_tokens, lang=tgt_code)
        return translations

# Example usage if run as script
if __name__ == "__main__":
    translator = IndicTrans2Translator()
    src_lang, tgt_lang = "English", "Hindi"
    input_sentences = [
        "When I was young, I used to go to the park every day.",
        "We watched a new movie last week, which was very inspiring.",
    ]
    translations = translator.translate(input_sentences, src_lang, tgt_lang)
    if translations:
        for input_sentence, translation in zip(input_sentences, translations):
            print(f"{src_lang}: {input_sentence}")
            print(f"{tgt_lang}: {translation}")
