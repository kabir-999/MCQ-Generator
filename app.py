import os
import fitz  # PyMuPDF for extracting text from PDFs
import json
from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from dotenv import load_dotenv
from flask_cors import CORS  # Flask-CORS import

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Apply CORS to the entire app
CORS(app)  # This will allow all origins, you can restrict it further if needed.

# Configure Gemini API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Set model configuration
generation_config = {
    "temperature": 0.8,
    "top_p": 0.9,
    "top_k": 40,
    "max_output_tokens": 8192,
}

model = genai.GenerativeModel(
    model_name="gemini-2.0-flash-exp",
    generation_config=generation_config,
    system_instruction="read the uploaded pdf and generate mcq's....each question's difficulty should be adjusted according to previous question...generate 10 questions and in the end classify score by saying how many easy, medium and difficult questions user got right. Format each question as:\n**Question:** <Question_Text>\n**Options:**\n(a) <Option_1>\n(b) <Option_2>\n(c) <Option_3>\n(d) <Option_4>\n**Answer:** <Correct_ans> (Write only the correct option text, no labels like 'a', 'b', etc.)"
)

# Function to extract text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as doc:
        for page in doc:
            text += page.get_text("text") + "\n"
    return text.strip()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate_mcqs", methods=["POST"])
def generate_mcqs():
    if "pdf_file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    pdf_file = request.files["pdf_file"]
    if pdf_file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    try:
        # Save PDF temporarily
        pdf_path = "uploaded.pdf"
        pdf_file.save(pdf_path)

        # Extract text from PDF
        extracted_text = extract_text_from_pdf(pdf_path)

        if not extracted_text:
            return jsonify({"error": "Could not extract text from the PDF"}), 400

        # Generate MCQs using Gemini AI
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(extracted_text)

        # Format MCQs properly
        mcqs = response.text.strip().split("\n\n")
        formatted_mcqs = []

        for mcq in mcqs:
            if "**Question:**" in mcq and "**Options:**" in mcq and "**Answer:**" in mcq:
                parts = mcq.split("**Options:**")
                question_part = parts[0].replace("**Question:**", "").strip()
                
                options_and_answer = parts[1].split("**Answer:**")
                options_part = options_and_answer[0].strip()
                answer_part = options_and_answer[1].strip()

                # Clean up options
                options = [opt.strip()[4:].strip() for opt in options_part.split("\n") if opt.strip()]
                
                # Ensure correct answer is one of the options
                answer_part = answer_part.strip().lower()
                options_cleaned = [opt.lower() for opt in options]

                if answer_part not in options_cleaned:
                    print(f"⚠ Warning: Correct answer '{answer_part}' not found in options {options_cleaned}")

                formatted_mcqs.append({
                    "question": question_part,
                    "options": options,
                    "answer": answer_part  # Store clean answer without extra formatting
                })

        return jsonify({"mcqs": formatted_mcqs})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
