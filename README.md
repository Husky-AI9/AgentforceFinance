# AgenforceFinance

Agentforce Finance is a Salesforce-native AI agent that automates core accounting workflows—extracting data from invoices and purchase orders, flagging anomalies, and generating forecasts.


# Deployment

To deploy the apex class
1. Clone the repo 
2. Go into SalesforceApp folder and open and cmd window
3. Type `sf project deploy start --target-org "YourOrgName"`

To deploy the backend
1. Copy the code in backend into a repo
2. Host it on render.com
3. Configure environment variable `GOOGLE_GENAI_API_KEY="Your Gemini API Key"` in your render project

# Features
**1. Natural-Language Q&A** – Users can ask any finance or accounting question in plain English. The agent taps into Salesforce records, policy documents, and historical transactions to deliver concise, citation-backed answers instantly, cutting research time from hours to seconds.


<img src="https://i.imgur.com/3FxZ7lU.gif" width="200px" height="200px"  alt="Demo GIF"/>


**2. Financial Document Summary & Number Extraction** – Upload PDFs (invoices, receipts, balance sheets) and let the agent extract all critical figures (amounts, dates, line items), then generate a structured summary with bullet lists of key numbers. This accelerates report reviews and ensures important metrics are never overlooked.


<img  src="https://i.imgur.com/MlSELPb.gif" alt="Demo GIF"/>


**3. Audit-Readiness Assistant** – Continuously evaluates uploaded documents and transaction logs against custom compliance checklists. It compiles risk-scored audit packets—extracting critical clauses and flagging potential issues—so audit teams spend less time assembling materials and more time driving insights.


<img  src="https://i.imgur.com/jBmldKz.gif" alt="Demo GIF"/>


**4. Time-Series Forecasting** – Ingest CSV datasets to produce both downloadable CSV forecasts and embedded PNG trend charts. Users can visualize future revenue, expenses, or cash flow directly in chat and export data for deeper analysis, improving budgeting accuracy and strategic planning.


<img  src="https://i.imgur.com/3mxokKc.gif"  alt="Demo GIF"/>


**5. Data Extraction** – A unified pipeline that pulls structured data (numeric and textual) from financial docs such as invoices, receipts, balance sheets, and P&Ls. By standardizing output into Salesforce records, it eliminates manual data entry, reduces errors, and powers downstream automations.


<img  src="https://i.imgur.com/dLxjwQs.gif" alt="Demo GIF"/>


**6. Invoice ↔ PO Comparison** – Automatically compares line-items between vendor invoices and purchase orders, highlighting mismatches in quantities, prices, or terms. Each discrepancy is explained in natural language, enabling procurement and finance teams to resolve issues faster and tighten controls.


<img  src="https://i.imgur.com/Ad9azjb.gif" alt="Demo GIF"/>


# License

MIT License Copyright (c)] Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions: The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software. THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
