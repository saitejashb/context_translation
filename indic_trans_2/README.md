# IndicTrans2 API

This project provides a high-performance, Dockerized REST API for the [IndicTrans2](https://github.com/AI4Bharat/IndicTrans2) model, capable of translating between English and 22 Indic languages. It is built using **FastAPI** and served via **Nginx**, with full **GPU support** for efficient inference.

## Features

*   **FastAPI Backend**: Robust and fast Python API framework.
*   **GPU Acceleration**: Optimized for NVIDIA GPUs using PyTorch with CUDA support.
*   **Dockerized**: Easy deployment with Docker and Docker Compose.
*   **Nginx Reverse Proxy**: Production-ready server configuration.
*   **Language Support**: Supports translation between English and 22 Indian languages.
*   **Customizable Generation**: Control over `max_length`, `num_beams`, and `num_return_sequences`.

## Prerequisites

*   **Docker Desktop** (Windows/Mac/Linux)
*   **NVIDIA Container Toolkit** (Required for GPU support)
*   **NVIDIA GPU** (Tested on RTX 5090, supports CUDA 12.x/13.x)

## Quick Start

1.  **Clone the repository:**
    ```bash
    git clone <repository-url>
    cd indicTrans2API
    ```

2.  **Set up Environment Variables:**
    Create a `.env` file in the root directory with your Hugging Face token (required to download the model):
    ```env
    HF_TOKEN=your_huggingface_token_here
    ```

3.  **Build and Run with Docker Compose:**
    ```bash
    docker-compose up --build
    ```
    This will:
    *   Build the API container.
    *   Start the API service on port `8001`.
    *   Start Nginx on port `8080`.

    *Note: The first run will take some time to download the model (~4GB).*

## Client Usage Example (Python)

Here is a quick example of how to use the API from a Python client:

```python
import requests

API_URL = "http://localhost:8080/translate"

payload = {
    "text": ["Hello, how are you?", "This is a test."],
    "src_lang": "English",
    "tgt_lang": "Hindi",
    "max_length": 512,       # (Optional) Max generation length
    "num_beams": 5,          # (Optional) Beam search size
    "num_return_sequences": 1 # (Optional) Number of translations per input
}

response = requests.post(API_URL, json=payload)
print(response.json())
# Output: {'translations': ['नमस्कार, आप कैसे हैं?', 'यह एक परीक्षण है।']}
```

### Available Arguments

| Argument | Type | Required | Default | Description |
| :--- | :--- | :--- | :--- | :--- |
| `text` | `str` or `List[str]` | Yes | - | Input text or list of sentences to translate. |
| `src_lang` | `str` | Yes | - | Source language name (e.g., "English"). |
| `tgt_lang` | `str` | Yes | - | Target language name (e.g., "Hindi"). |
| `max_length` | `int` | No | 512 | Maximum length of the generated translation. |
| `num_beams` | `int` | No | 5 | Number of beams for beam search. Higher is better quality but slower. |
| `num_return_sequences` | `int` | No | 1 | Number of translation variations to return. |

## API Documentation

The API is accessible at `http://localhost:8001` (Direct) or `http://localhost:8080` (via Nginx).

### 1. Get Supported Languages

**Endpoint:** `GET /languages`

Returns a map of supported language names to their internal codes.

**Response:**
```json
{
  "Assamese": "asm_Beng",
  "Bengali": "ben_Beng",
  "English": "eng_Latn",
  "Hindi": "hin_Deva",
  ...
}
```

### 2. Translate Text

**Endpoint:** `POST /translate`

Translates a list of sentences from source to target language.

**Request Body:**
```json
{
  "text": ["Hello, how are you?", "This is a test."],
  "src_lang": "English",
  "tgt_lang": "Hindi",
  "max_length": 512,    # Optional (default: 512)
  "num_beams": 5,       # Optional (default: 5)
  "num_return_sequences": 1 # Optional (default: 1)
}
```

**Response:**
```json
{
  "translations": [
    "नमस्कार, आप कैसे हैं?",
    "यह एक परीक्षण है।"
  ]
}
```

## Development Setup (Local)

If you wish to run the code locally without Docker:

1.  **Create a virtual environment:**
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    # source venv/bin/activate # Linux/Mac
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    *Note: Ensure you install the correct PyTorch version for your CUDA version.*

3.  **Run the API:**
    ```bash
    uvicorn app:app --host 0.0.0.0 --port 8001
    ```

## Testing

A test script is provided to verify the API endpoints:

```bash
python test_inference.py
```
Ensure the API is running before executing the test script.

## Project Structure

*   `app.py`: FastAPI application entry point.
*   `inference.py`: Core translation logic and model loading.
*   `languages.py`: Language code mappings.
*   `Dockerfile`: Container definition for the API.
*   `docker-compose.yml`: Service orchestration.
*   `nginx.conf`: Nginx configuration.
*   `requirements.txt`: Python dependencies.
