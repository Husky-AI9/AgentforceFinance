import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai

# Pydantic model to parse incoming request data
class ChatbotRequest(BaseModel):
    question: str

# Load the API key from environment variable
api_key = os.environ.get("GOOGLE_GENAI_API_KEY")
if not api_key:
    raise ValueError("Environment variable 'GOOGLE_GENAI_API_KEY' is not set.")

# Initialize the genAI client
client = genai.Client(api_key=api_key)


from fastapi import FastAPI, Query
import requests
from google import genai
from docling.document_converter import DocumentConverter

app = FastAPI()

# Instantiate the genai client with your API key
client = genai.Client(api_key="YOUR_API_KEY_HERE")

def download_and_convert_to_markdown(pdf_url: str) -> str:
    response = requests.get(pdf_url)
    response.raise_for_status()  # Raises an exception if the download fails
    pdf_filename = "temp_document.pdf"
    with open(pdf_filename, "wb") as f:
        f.write(response.content)
    converter = DocumentConverter()
    conversion_result = converter.convert(pdf_filename)
    document_markdown = conversion_result.document.export_to_markdown()
    
    return document_markdown

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

@app.post("/analyze_document")
def analyze_document(url: str = Query(..., description="Downloadable URL to a PDF document")):
    
    document_markdown = download_and_convert_to_markdown(url)

    # 4. Construct the prompt for the generative model
    instruction = f"""
    The text below is scanned from a document, {url}, into markdown format. 
    You are an expert accountant and knowledgeable in financing.
    Summarize the document and extract all important numbers in this document.
    
    Document Text:
    {document_markdown}
    """

    # 5. Use the genai client to summarize and extract the data
    try:
        ai_response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=instruction,
        )
        result_text = ai_response.text
    except Exception as e:
        return {"error": f"Failed to generate AI response: {e}"}

    # 6. Return the summarized text and extracted information
    return {
        "response": result_text
    }
