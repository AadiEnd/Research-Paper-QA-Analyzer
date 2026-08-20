# Research Paper QA Analyzer

A Flask web app that takes a research paper (PDF, DOCX, or TXT), summarizes it, and generates multiple-choice questions (MCQs) from its content using Google's Gemini API. Results can be viewed in the browser and downloaded as a `.txt` or `.pdf` file.

## Features

- Upload a research paper in PDF, DOCX, or TXT format
- Extracts text from the uploaded file
- Generates an academic summary (topic, objective, methodology, key findings, conclusion)
- Generates a configurable number of multiple-choice questions with answers, based strictly on the paper's content
- Download results as a text file or a formatted PDF

## Project Structure

```
Research Paper QA Analyzer/
├── app.py              # Main Flask application
├── templates/
│   ├── index.html      # Upload form
│   └── results.html    # Displays summary + MCQs, with download links
├── uploads/             # Uploaded source files (created automatically)
├── results/             # Generated .txt and .pdf outputs (created automatically)
└── README.md
```

## Requirements

- Python 3.9+
- The following Python packages:
  - `flask`
  - `pdfplumber`
  - `python-docx`
  - `google-generativeai`
  - `fpdf2`
  - `werkzeug`

Install them with:

```bash
pip install flask pdfplumber python-docx google-generativeai fpdf2 werkzeug
```

(Consider freezing these into a `requirements.txt` with `pip freeze > requirements.txt` once your environment is set up.)

## Setup

1. Clone or download this repository.
2. Install the dependencies listed above (ideally inside a virtual environment).
3. Set your Google Gemini API key as an environment variable instead of hardcoding it in `app.py`:

   ```bash
   # macOS/Linux
   export GOOGLE_API_KEY="your-api-key-here"

   # Windows (PowerShell)
   setx GOOGLE_API_KEY "your-api-key-here"
   ```

   > **Security note:** `app.py` currently has an API key hardcoded directly in the source (`os.environ["GOOGLE_API_KEY"] = "..."`). This is a security risk, especially if the code is ever shared or pushed to a public repository. Remove the hardcoded key and load it from the environment instead, e.g.:
   > ```python
   > genai.configure(api_key=os.environ["GOOGLE_API_KEY"])
   > ```
   > If this key has already been shared or committed anywhere, revoke/rotate it in your Google AI Studio / Cloud console.

4. Run the app:

   ```bash
   python app.py
   ```

5. Open your browser to `http://127.0.0.1:5000/`.

## Usage

1. On the homepage, upload a PDF, DOCX, or TXT research paper and specify the number of MCQs to generate.
2. Submit the form — the app extracts the text and sends it to the Gemini model for summarization and MCQ generation.
3. View the generated summary and MCQs on the results page.
4. Download the results as `.txt` or `.pdf` using the provided links.

## Notes

- Uploaded files are saved to the `uploads/` folder, and generated outputs are saved to the `results/` folder. Both are created automatically on first run if they don't exist.
- The app currently references the model `gemini-3.5-flash` — verify this model name is valid for your API access, and update it in `app.py` if needed.
- This app runs in Flask's debug mode by default (`app.run(debug=True)`), which is convenient for development but should be disabled before any production deployment.

## License

Add a license of your choice here (e.g., MIT).
