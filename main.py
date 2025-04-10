import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
import requests
from fastapi import FastAPI, Query
import tempfile

# Pydantic model to parse incoming request data
class ChatbotRequest(BaseModel):
    question: str

class DocumentRequest(BaseModel):
    url: str

class InvoiceInput(BaseModel):
    invoice_url: str
    purchase_order_url: str

# Load the API key from environment variable
api_key = os.environ.get("GOOGLE_GENAI_API_KEY")
if not api_key:
    raise ValueError("Environment variable 'GOOGLE_GENAI_API_KEY' is not set.")

# Initialize the genAI client
client = genai.Client(api_key=api_key)

app = FastAPI()

def download_document(pdf_url: str) -> str:

    response = requests.get(pdf_url, stream=True)
    response.raise_for_status()  # Raise an exception for any HTTP errors    
    filename = "Temporary_File.pdf"
    with open(filename, "wb") as f:
        f.write(response.content)
    return filename

def financeChatbot(question: str) -> str:
    instruction = f"""
    You are a financial markets tutor and adviser designed to educate and recommend/advise users about investing, 
    financial instruments/documents, and accounting concepts.
    Answer briefly and to the point, don't explain unnecessarily, and use real life examples that users can relate to.
    Capabilities:
    - Teach financial concepts in an interactive and engaging way.
    - Explain investment strategies, risk management, and portfolio diversification but only when asked.
    - Answer questions related to fundamentals of accounting and financing.
    Guidelines:
    - Provide structured, step-by-step explanations with examples.
    - Use simple language and try to give responses with relpipevant examples.

    The user question: {question}
    """

    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=instruction,
        )
        return response.text
    except Exception as e:
        print(f"Error generating content: {e}")
        return "An error occurred while processing the request."

app = FastAPI()

@app.post("/finance-chatbot")
def finance_chatbot_endpoint(request: ChatbotRequest):
    if not request.question:
        raise HTTPException(status_code=400, detail="Question field is missing.")
    
    answer = financeChatbot(request.question)
    return {"answer": answer}

@app.post("/analyze-document")
def analyze_document(request: DocumentRequest):
    
    pdf_url = request.url
    filename = download_document(pdf_url)
    sample_pdf = client.files.upload(file=filename)

    instruction = f"""You are an expert accountant and knowledgeable in financing.
    Summarize the document and extract all important numbers in this document.
    """

    ai_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[instruction, sample_pdf],
        )
    result_text = ai_response.text

    return {
        "response": result_text
    }

@app.post("/analyze-risk")
def analyze_document(request: DocumentRequest):
    
    pdf_url = request.url
    filename = download_document(pdf_url)
    sample_pdf = client.files.upload(file=filename)

    instruction = f"""Your are an expert accountant and knowledgeable in financing. I want you do the following with the inputed document text.
                    
                    Task:
                        _Analyze the provided financial statements and contract documents for potential non-compliance, fraud, or high-risk issues.
                        _Identify suspicious expenses, tax vulnerabilities, IFRS/GAAP gaps, and problematic vendor terms.
                        _Summarize each finding clearly, referencing specific data or clauses.
                        _Recommend practical actions or changes to address the identified risks.

                        Output:
                        _A brief list of issues with direct references to the source documents.
                        _A short explanation of how each issue might indicate fraud, tax exposure, or accounting compliance problems.
                        _Clear next steps or best practices to mitigate and prevent each risk.
    """

    ai_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[instruction, sample_pdf],
        )
    result_text = ai_response.text

    return {
        "response": result_text
    }




@app.post("/analyze-invoice")
async def analyze_invoice(data: InvoiceInput):
    # Download the invoice PDF
    try:
        invoice_resp = requests.get(data.invoice_url)
        invoice_resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading invoice file: {e}")

    # Download the purchase order PDF
    try:
        po_resp = requests.get(data.purchase_order_url)
        po_resp.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading purchase order file: {e}")

    # Save both files to temporary locations.
    try:
        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_invoice:
            temp_invoice.write(invoice_resp.content)
            invoice_filepath = temp_invoice.name

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_po:
            temp_po.write(po_resp.content)
            po_filepath = temp_po.name
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving temporary files: {e}")

    # Upload the files to Gemini.
    try:
        invoice_doc = client.files.upload(file=invoice_filepath)
        purchase_order_doc = client.files.upload(file=po_filepath)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error uploading files to Gemini: {e}")
    finally:
        # Clean up temporary files.
        os.remove(invoice_filepath)
        os.remove(po_filepath)

    # Define a detailed prompt to instruct the model.
    prompt = (
        "You are a finance assistant who processes invoices and purchase orders. "
        "The first document is a supplier invoice and the second is an internal purchase order. "
        "Extract the following details from the invoice: vendor name, invoice number, invoice date, due date, and total amount. "
        "Also, extract the following details from the purchase order: vendor name, purchase order number, order date, total amount, and item details. "
        "Compare the two documents and provide a plain text summary suitable for a chat window. "
        "Format your answer using clear headings and bullet points to list the extracted information and highlight any discrepancies, such as mismatches in amounts or missing items. "
        "Do not output JSON; instead, produce a narrative summary."
    )

    # Generate the human-readable summary.
    try:
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[invoice_doc, purchase_order_doc, prompt]
        )
        result_text = response.text
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating content: {e}")

    return {"result": result_text}