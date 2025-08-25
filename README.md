# AI-Powered Health Report Assistant

## Overview

AI-Powered Health Report Assistant is a web app built using Streamlit that helps users interpret medical reports by combining OCR, anomaly detection, and LLM-powered plain-language explanations.

It simplifies healthcare understanding by converting complex lab data into meaningful insights and general lifestyle tips — no medical degree required.

---

## Key Features

### 1. Medical Report Upload
- Supports PDF uploads (typed or scanned).
- Automatically detects whether OCR is needed.

### 2. OCR + Text Extraction
- Uses PyMuPDF for text-based PDFs.
- Falls back to pytesseract + pdf2image for image-based scans.

### 3. Abnormality Detection
- Parses lab values using regex and matches against predefined normal ranges.
- Flags low/high test values with clear explanations.

### 4. AI Summary Generation
- Uses Groq's LLaMA 3 (LLaMA3-70B) model for fast, high-quality natural-language summary of the report.
- Summary includes abnormal values, their meaning, and general tips.

### 5. Medical Q&A Chatbot
- A Retrieval-Augmented Generation (RAG) chatbot using:
  - FAISS for vector search
  - LangChain with HuggingFace embeddings
  - GROQ for answering context-based medical questions
- Users can export chat history as PDF.

### 6. Clean UI
- Built with custom dark-themed CSS for modern look and feel.
- Offers navigation, loading states, download buttons, and disclaimers.

---

## Setup Instructions

### 1. Install Python dependencies
```
pip install -r requirements.txt
```

### 2. Configure API keys
Create a `.env` file with the following content:
```
GROQ_API=your_groq_api_key
```

### 3. Run the app
```
streamlit run home.py
```

---

## Suggested Folder Structure

```
AI-Health-Assistant
├── home.py                  # Main navigation + home layout
├── hack.py                 # Report analyzer
├── medibot.py              # Medical chatbot
├── assets/                 # Logo and screenshots
│   └── screenshots/
├── vectorstore/            # FAISS vector DB
├── .env                    # API keys
├── requirements.txt
└── README.md
```

---



## Disclaimer

This application is not a medical device. It provides educational health insights and summaries. Always consult a licensed medical professional before making decisions based on your health report.