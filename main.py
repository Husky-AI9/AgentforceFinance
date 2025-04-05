import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
import requests
from fastapi import FastAPI, Query

# Pydantic model to parse incoming request data
class ChatbotRequest(BaseModel):
    question: str

class DocumentRequest(BaseModel):
    url: str

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
