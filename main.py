import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from google import genai
import requests
from fastapi import FastAPI, Query
import tempfile
import pandas as pd
import matplotlib.pyplot as plt
from darts import TimeSeries
from darts.models import ARIMA
from fastapi.responses import StreamingResponse

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


def forecast_from_csv(csv_file: str,
                      time_col: str,
                      value_col: str,
                      prediction_steps: int = 12,
                      png_filename: str = "forecast.png",
                      forecast_csv_filename: str = "forecasted.csv") -> None:
    """
    Reads a CSV file with time series data, fits an ARIMA model using Darts, forecasts a specified
    number of future time steps, and saves:
      - a forecast plot as a PNG file, and 
      - a new CSV file that contains both the historical and forecasted data (with the date column included).
      
    The plot includes both the historical data and the forecast data with a connecting line between the last
    historical point and the first forecast point.
    
    Parameters:
        csv_file (str): Local path to the CSV file.
        time_col (str): Name of the column with date/time information.
        value_col (str): Name of the revenue/value column.
        prediction_steps (int): Number of future time steps to forecast.
        png_filename (str): Filename for the generated PNG plot.
        forecast_csv_filename (str): Filename for the CSV with forecast appended.
    """
    # Read the CSV file and create a Darts TimeSeries object.
    df = pd.read_csv(csv_file, parse_dates=[time_col])
    print("Data read from CSV:")
    print(df.head())
    series = TimeSeries.from_dataframe(df, time_col, value_col)
    
    # Fit an ARIMA model to the historical data and forecast future values.
    model = ARIMA()
    model.fit(series)
    forecast = model.predict(prediction_steps)
    
    # Plot the historical data and forecast.
    plt.figure(figsize=(10, 6))
    series.plot(label='Historical Data')
    forecast.plot(label='Forecast', color="blue")
    
    # Connect the last historical point with the first forecast point.
    last_hist_date = series.time_index[-1]
    first_fc_date = forecast.time_index[0]
    last_hist_value = series.values()[-1][0]   # Univariate series assumed.
    first_fc_value = forecast.values()[0][0]
    plt.plot([last_hist_date, first_fc_date],
             [last_hist_value, first_fc_value],
             color="blue", linewidth=2)
    
    plt.title(f"Time Series {value_col} Forecast")
    plt.xlabel(f"{time_col}")
    plt.ylabel(f"{value_col}")
    plt.legend()
    
    # Save the plot as a PNG file.
    plt.savefig(png_filename)
    plt.close()
    
    # Append the forecasted data to the historical data.
    complete_series = series.append(forecast)
    df_complete = complete_series.pd_dataframe().reset_index().rename(columns={'index': time_col})
    df_complete.to_csv(forecast_csv_filename, index=False)


@app.post("/forecast")
async def forecast_endpoint(
    csv_url: str = Form(...),
    time_col: str = Form(...),
    value_col: str = Form(...),
    prediction_steps: int = Form(12)
):
    """
    Endpoint to perform time series forecasting.
    
    Accepts:
      - **csv_url**: A downloadable URL link pointing to the CSV file containing the time series data.
      - **time_col**: The name of the date/time column in the CSV.
      - **value_col**: The name of the revenue/value column in the CSV.
      - **prediction_steps**: The number of future time steps to forecast (default is 12).
    
    The endpoint downloads the CSV, processes it to generate a forecast plot and a forecast CSV,
    and returns the PNG plot as a downloadable file.
    """
    # Download the CSV file from the provided URL.
    try:
        response = requests.get(csv_url)
        response.raise_for_status()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error downloading CSV: {str(e)}")
    
    download_filename = "downloaded_timeseries.csv"
    with open(download_filename, "wb") as f:
        f.write(response.content)
    
    # Define the output filenames.
    forecast_png = "forecast.png"
    forecast_csv = "forecasted.csv"
    
    try:
        # Run forecasting to generate the PNG and CSV.
        forecast_from_csv(download_filename, time_col, value_col, prediction_steps,
                          png_filename=forecast_png,
                          forecast_csv_filename=forecast_csv)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating forecast: {str(e)}")
    
    # Return the PNG file as a downloadable image.
    try:
        png_file = open(forecast_png, "rb")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading forecast PNG: {str(e)}")
    
    return StreamingResponse(png_file,
                             media_type="image/png",
                             headers={"Content-Disposition": "attachment; filename=forecast.png"})


@app.get("/forecast_csv")
async def forecast_csv_endpoint():
    """
    Endpoint to download the forecast CSV file generated by the /forecast endpoint.
    This should be called after /forecast has been executed so that the CSV file exists.
    """
    csv_filename = "forecasted.csv"
    if not os.path.exists(csv_filename):
        raise HTTPException(status_code=404, detail="Forecast CSV file not found. Please run /forecast first.")
    try:
        csv_file = open(csv_filename, "rb")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading forecast CSV: {str(e)}")
    
    return StreamingResponse(csv_file,
                             media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=forecasted.csv"})