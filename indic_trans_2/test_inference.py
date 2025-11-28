import requests
import json

# Using port 8080 (Nginx) which proxies to 8001 (FastAPI)
BASE_URL = "http://localhost:8080" 

def test_get_languages():
    print("Testing GET /languages...")
    try:
        response = requests.get(f"{BASE_URL}/languages")
        response.raise_for_status()
        languages = response.json()
        print("Successfully retrieved languages.")
        print("Supported languages:")
        for lang, code in languages.items():
            print(f"  {lang}: {code}")
    except Exception as e:
        print(f"Failed to get languages: {e}")

def test_translate():
    print("\nTesting POST /translate...")
    payload = {
        "text": [
            "Hello, how are you?",
            "This is a test sentence."
        ],
        "src_lang": "English",
        "tgt_lang": "Hindi"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/translate", json=payload)
        response.raise_for_status()
        result = response.json()
        translations = result.get("translations", [])
        
        for src, tgt in zip(payload["text"], translations):
            print(f"{src} -> {tgt}")
            
    except Exception as e:
        print(f"Failed to translate: {e}")
        if hasattr(e, 'response') and e.response is not None:
             print(f"Response content: {e.response.text}")

def test_translate_custom_params():
    print("\nTesting POST /translate with custom parameters...")
    payload = {
        "text": ["This is a generated sentence."],
        "src_lang": "English",
        "tgt_lang": "Hindi",
        "max_length": 50,
        "num_beams": 3
    }
    
    try:
        response = requests.post(f"{BASE_URL}/translate", json=payload)
        response.raise_for_status()
        result = response.json()
        translations = result.get("translations", [])
        
        for src, tgt in zip(payload["text"], translations):
            print(f"{src} -> {tgt}")
            
    except Exception as e:
        print(f"Failed to translate with custom params: {e}")

if __name__ == "__main__":
    print(f"Targeting API at: {BASE_URL}")
    test_get_languages()
    test_translate()
    test_translate_custom_params()
