from flask import Flask, request, render_template, redirect, url_for
import pytesseract
from PIL import Image
import PyPDF2

app = Flask(__name__)

# Temporary storage for summary (clears after refresh)
last_summary = None


# --------------------------------------------
# Extract text from PDF
# --------------------------------------------
def extract_pdf_text(file):
    try:
        reader = PyPDF2.PdfReader(file)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
        return text.strip() or "No text found in PDF."
    except:
        return "Error reading PDF."


# --------------------------------------------
# Extract text from image using OCR
# --------------------------------------------
def extract_image_text(file):
    try:
        image = Image.open(file)
        return pytesseract.image_to_string(image)
    except:
        return "Error processing image."


# --------------------------------------------
# Summary generator (50, 100, 200 lines)
# --------------------------------------------
def generate_summary(text, length="short"):
    sentences = [s.strip() for s in text.split(".") if s.strip()]
    if not sentences:
        return "No readable text found."

    if length == "short":
        return ". ".join(sentences[:50])
    elif length == "medium":
        return ". ".join(sentences[:100])
    else:
        return ". ".join(sentences[:200])


# --------------------------------------------
# Home page — summary should disappear after refresh
# --------------------------------------------
@app.route("/")
def home():
    global last_summary
    summary = last_summary
    last_summary = None  # clears summary after loading once
    return render_template("index.html", summary=summary)


# --------------------------------------------
# Upload route — POST → REDIRECT → GET
# --------------------------------------------
@app.route("/upload", methods=["POST"])
def upload():
    global last_summary

    if "file" not in request.files:
        last_summary = "No file uploaded."
        return redirect(url_for("home"))

    file = request.files["file"]
    filename = file.filename.lower()

    if not filename:
        last_summary = "Invalid file."
        return redirect(url_for("home"))

    # Decide extraction method
    if filename.endswith(".pdf"):
        text = extract_pdf_text(file)
    elif filename.endswith((".png", ".jpg", ".jpeg")):
        text = extract_image_text(file)
    else:
        last_summary = "Unsupported file type."
        return redirect(url_for("home"))

    # Generate summary
    length = request.form.get("length", "short")
    last_summary = generate_summary(text, length)

    return redirect(url_for("home"))


# --------------------------------------------
# Force browser to not cache summary
# --------------------------------------------
@app.after_request
def add_no_cache_headers(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    return response


# --------------------------------------------
# Run the app
# --------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)
