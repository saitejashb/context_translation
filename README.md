# DOCX Translation Tool - English to Telugu

This tool uses IndicTransToolkit to translate DOCX (Word) documents from English to Telugu.

## Prerequisites

- Python >= 3.8
- Git (to clone the repository)
- GPU (optional, but recommended for faster translation)

## Installation

### Windows (PowerShell)

1. Run the setup script:
   ```powershell
   .\setup_environment.ps1
   ```

### Linux/Mac (Bash)

1. Make the script executable:
   ```bash
   chmod +x setup_environment.sh
   ```

2. Run the setup script:
   ```bash
   ./setup_environment.sh
   ```

### Manual Installation

1. Clone the IndicTransToolkit repository (if not already done):
   ```bash
   git clone https://github.com/VarunGumma/IndicTransToolkit.git
   ```

2. Create a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   
   # Linux/Mac
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install IndicTransToolkit:
   ```bash
   cd IndicTransToolkit
   pip install --editable ./
   cd ..
   ```

4. Install other requirements:
   ```bash
   pip install -r requirements.txt
   ```

5. Upgrade protobuf to >= 5.0.0 (required for IndicTrans2):
   ```bash
   pip install --upgrade "protobuf>=5.0.0"
   ```

## Usage

### Test the Installation

First, test that everything is working correctly:

1. Activate the virtual environment:
   ```powershell
   # Windows
   .\venv\Scripts\Activate.ps1
   
   # Linux/Mac
   source venv/bin/activate
   ```

2. Run the test script:
   ```bash
   python test_translation.py
   ```

   This will translate a few sample English sentences to Telugu to verify the setup.

### Translate DOCX Files

1. Activate the virtual environment (if not already activated)

2. Run the translation script:
   ```bash
   python translate_docx.py input_file.docx
   ```

   This will create a file named `input_file_telugu.docx` in the same directory.

### Specify Output File

```bash
python translate_docx.py input_file.docx output_file.docx
```

### Example

```bash
python translate_docx.py document.docx translated_document.docx
```

## Features

- Translates entire DOCX documents from English to Telugu
- **Glossary support**: Automatically uses domain-specific terms from `glossary.csv`
- Preserves document structure (paragraphs, tables, headers, footers)
- Handles batch translation for efficiency
- Supports both GPU and CPU execution
- Case-insensitive glossary matching (works with capitals or small letters)
- Automatically generates output filename if not specified

## How It Works

1. The script loads the `ai4bharat/indictrans2-en-indic-1B` model
2. Loads glossary terms from `glossary.csv` (if available)
3. Reads the input DOCX file
4. Extracts text from:
   - Paragraphs
   - Tables
   - Headers
   - Footers
5. For each text segment:
   - Identifies glossary terms (case-insensitive)
   - Replaces glossary terms with placeholders
   - Translates remaining text with NMT model
   - Restores glossary terms with Telugu translations
6. Replaces the original text with translations
7. Saves the translated document

### Glossary Integration

The system automatically uses terms from `glossary.csv` when translating:
- Glossary terms are matched case-insensitively
- Longer phrases are matched first to avoid partial matches
- Glossary translations take priority over NMT translations
- Terms like "G.O.RT.NO.", "GOVERNMENT", "ORDER" etc. are automatically translated using the glossary

## Web Interface

A web interface is available for easy file upload and translation!

### Starting the Web Service

1. Activate the virtual environment:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

2. Install Flask (if not already installed):
   ```powershell
   pip install flask werkzeug
   ```

3. Start the web server:
   ```powershell
   python app.py
   ```
   
   Or use the startup script:
   ```powershell
   .\start_web_app.ps1
   ```

4. Open your browser and go to: **http://localhost:5000**

5. Upload a DOCX file and click "Translate to Telugu"

The web interface features:
- Drag and drop file upload
- Real-time translation progress
- Automatic file download
- Clean, modern UI
- File size validation (max 50MB)

## Notes

- First run will download the model (~2GB), which may take some time
- Translation speed depends on your hardware (GPU recommended)
- Large documents may take significant time to translate
- The model uses beam search (num_beams=5) for better translation quality
- The web service loads the model on first request (may take a minute)

## Troubleshooting

### GPU Not Available
The script will automatically fall back to CPU if GPU is not available. Translation will be slower but will still work.

### Memory Issues
If you encounter out-of-memory errors:
- Close other applications
- Process smaller documents
- Reduce batch size in the script

### Model Download Issues
If model download fails:
- Check your internet connection
- Ensure you have sufficient disk space (~2GB)
- Try running the script again

### Adaptive Translation Same as Standard
If adaptive translation produces the same output as standard translation:

1. **Check GCS Glossary Permissions:**
   ```powershell
   python check_glossary_permissions.py
   ```
   This will check if the service account has proper permissions and provide setup instructions.

2. **Required Permissions:**
   - **Storage Object Viewer** role on bucket `glossaryp7`
   - **Cloud Translation API Editor** role on the project
   
3. **Grant Permissions:**
   - Go to [Google Cloud Console IAM](https://console.cloud.google.com/iam-admin/iam)
   - Find service account: `translation-bot-v2@concise-memory-477512-u4.iam.gserviceaccount.com`
   - Add roles: `Storage Object Viewer` and `Cloud Translation API Editor`
   - Or run the permissions checker script for detailed instructions

4. **After Fixing Permissions:**
   - The glossary will be automatically created on first use
   - Adaptive translation will then use the GCS glossary and produce different results

## License

This tool uses IndicTransToolkit, which is subject to its own license terms.

