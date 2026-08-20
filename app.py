from flask import Flask, request, render_template, send_file
import os
import pdfplumber
import docx
from werkzeug.utils import secure_filename
import google.generativeai as genai
from fpdf import FPDF


# Set your API key
os.environ["GOOGLE_API_KEY"] = "AQ.Ab8RN6J5YIR8pdr5ZpALW-h1OX6fdLLpaxbXyexkrBq7wnJYdA"

genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

model = genai.GenerativeModel("gemini-3.5-flash")


app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['RESULTS_FOLDER'] = 'results'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'txt', 'docx'}


# Custom functions

def allowed_file(filename):
     return (
          '.' in filename
          and filename.rsplit('.', 1)[1].lower()
          in app.config['ALLOWED_EXTENSIONS']
     )


def extract_text_file(file_path):

     ext = file_path.rsplit(".", 1)[1].lower()

     if ext == "pdf":

          with pdfplumber.open(file_path) as pdf:
               text = '\n'.join([
                    page.extract_text() or ""
                    for page in pdf.pages
               ])

          return text

     elif ext == "docx":

          doc = docx.Document(file_path)

          text = '\n'.join([
               para.text
               for para in doc.paragraphs
          ])

          return text

     elif ext == "txt":

          with open(file_path, 'r', encoding='utf-8') as file:
               return file.read()

     return None


def Questions_mcqs_generator(input_text, num_questions):

     prompt = f"""
You are an expert academic research analyst and professional MCQ generator.

Analyze the following research paper text:

RESEARCH PAPER TEXT:
{input_text}

Generate a professional and concise summary using only information from the provided research paper. Do not add external information, assumptions, opinions, or unnecessary details.

Then generate exactly {num_questions} high-quality multiple-choice questions based strictly on the research paper.

OUTPUT FORMAT:

## SUMMARY

Title/Topic:
[Main topic]

Objective:
[Main research objective]

Methodology:
[Research methodology]

Key Findings:
[Important findings]

Conclusion:
[Main conclusion]

Professional Summary:
[Concise academic summary]


## MCQ

Question 1:
[Question]

A. [Option A]
B. [Option B]
C. [Option C]
D. [Option D]

Correct Answer: [A/B/C/D]


Generate exactly {num_questions} questions.

Return only the formatted summary and MCQs. Do not include greetings, disclaimers, external information, or additional commentary.
"""

     response = model.generate_content(prompt)

     return response.text


def save_mcqs_to_file(mcqs, filename):

     result_path = os.path.join(
          app.config['RESULTS_FOLDER'],
          filename
     )

     with open(result_path, 'w', encoding='utf-8') as file:
          file.write(mcqs)

     return result_path


def create_pdf(mcqs, filename):

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Replace common Unicode characters with Latin-1-safe characters
    safe_text = (
        mcqs
        .replace("\u2019", "'")   # Right curly apostrophe
        .replace("\u2018", "'")   # Left curly apostrophe
        .replace("\u201c", '"')   # Left double quote
        .replace("\u201d", '"')   # Right double quote
        .replace("\u2013", "-")   # En dash
        .replace("\u2014", "-")   # Em dash
        .replace("\u2026", "...") # Ellipsis
    )

    for mcq in safe_text.split("## MCQ"):

        if mcq.strip():
            pdf.multi_cell(0, 10, mcq.strip())
            pdf.ln(5)

    pdf_path = os.path.join(
        app.config["RESULTS_FOLDER"],
        filename
    )

    pdf.output(pdf_path)

    return pdf_path


# Routes

@app.route("/")
def index():
     return render_template('index.html')


@app.route("/generate", methods=["POST"])
def generate_mcqs():

     if 'file' not in request.files:
          return "No file part"

     file = request.files['file']

     if not file.filename:
          return "No file selected"

     if file and allowed_file(file.filename):

          filename = secure_filename(file.filename)

          file_path = os.path.join(
               app.config['UPLOAD_FOLDER'],
               filename
          )

          file.save(file_path)

          # Extract PDF, TXT, or DOCX text
          text = extract_text_file(file_path)

          if not text or not text.strip():
               return "Could not extract text from the uploaded file."

          num_questions = int(
               request.form['num_questions']
          )

          mcqs = Questions_mcqs_generator(
               text,
               num_questions
          )

          # Save generated MCQs
          base_filename = filename.rsplit('.', 1)[0]

          txt_filename = (
               f"generated_mcqs_{base_filename}.txt"
          )

          pdf_filename = (
               f"generated_mcqs_{base_filename}.pdf"
          )

          save_mcqs_to_file(
               mcqs,
               txt_filename
          )

          create_pdf(
               mcqs,
               pdf_filename
          )

          # Display and allow downloading
          return render_template(
               'results.html',
               mcqs=mcqs,
               txt_filename=txt_filename,
               pdf_filename=pdf_filename
          )

     return "Invalid File Format"


@app.route("/download/<filename>")
def download_file(filename):

     filename = secure_filename(filename)

     file_path = os.path.join(
          app.config['RESULTS_FOLDER'],
          filename
     )

     return send_file(
          file_path,
          as_attachment=True
     )


# Create required folders and run Flask

if __name__ == "__main__":

     if not os.path.exists(app.config['UPLOAD_FOLDER']):
          os.makedirs(app.config['UPLOAD_FOLDER'])

     if not os.path.exists(app.config['RESULTS_FOLDER']):
          os.makedirs(app.config['RESULTS_FOLDER'])

     app.run(debug=True)