# Bharat Voice AI

**AI-Powered WhatsApp Business Assistant for Indian SMBs**

Bharat Voice AI is a Retrieval-Augmented Generation (RAG) powered WhatsApp assistant that enables businesses to automatically answer customer queries using their own documents, knowledge base, and business information.

Instead of requiring customers to install an app or learn a new interface, Bharat Voice AI works directly inside WhatsApp, allowing businesses to provide instant, context-aware responses in Hindi, English, and Hinglish.

---

## Problem Statement

Small businesses receive repetitive customer queries every day:

* What are your timings?
* Do you provide home delivery?
* What are your membership plans?
* Where is your store located?
* Are you open on Sundays?

Most businesses answer these questions manually, resulting in delayed responses and lost customer engagement.

Bharat Voice AI automates these interactions using AI, RAG, and business-specific knowledge.

---

## Architecture

Customer sends a WhatsApp message

↓

Meta WhatsApp Business Platform

↓

Webhook (FastAPI / Flask)

↓

Query Processing

↓

RAG Pipeline (LangChain + ChromaDB)

Business Documents, FAQs, Services, Pricing, Policies

↓

LLM Response Generation (Groq + Llama 3.1 8B)

↓

WhatsApp Response

↓

Customer Receives AI-Powered Answer

---

## Tech Stack

| Layer               | Technology                      |
| ------------------- | ------------------------------- |
| Messaging Platform  | Meta WhatsApp Business Platform |
| Backend             | Python                          |
| API Framework       | FastAPI / Flask                 |
| LLM                 | Groq + Llama 3.1 8B             |
| Embeddings          | HuggingFace all-MiniLM-L6-v2    |
| Vector Database     | ChromaDB                        |
| RAG Framework       | LangChain                       |
| Document Processing | PDF / TXT / DOCX                |
| Deployment          | Render                          |
| Version Control     | Git + GitHub                    |

---

## Features

### AI-Powered Business Knowledge Assistant

* Answers questions based on business-specific documents
* Context-aware responses using RAG
* Reduces repetitive customer support work

### WhatsApp Integration

* No mobile app required
* Customers interact through WhatsApp
* Familiar interface with zero learning curve

### Document-Based Knowledge Base

* PDF support
* TXT support
* DOCX support
* Dynamic knowledge retrieval

### Multilingual Support

* English
* Hindi
* Hinglish

### RAG Grounding

* Answers generated from business data
* Reduced hallucinations
* Accurate business information retrieval

---

## Example Use Cases

### Medical Store

Customer:

> Do you provide home delivery?

AI:

> Yes, we provide home delivery within a 5 km radius.

---

### Gym

Customer:

> What is the monthly membership fee?

AI:

> Our monthly membership plan starts from ₹1500.

---

### Coaching Institute

Customer:

> Are admissions open?

AI:

> Yes, admissions for the upcoming batch are currently open.

---

## Setup

```bash
git clone https://github.com/HarshAlreja/BharatVoice
cd bharatvoice-ai

pip install -r requirements.txt

cp .env.example .env

# Add your API keys

python app.py
```

---

## Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_key

META_ACCESS_TOKEN=your_key

META_PHONE_NUMBER_ID=your_id

META_VERIFY_TOKEN=your_token

SARVAM_API_KEY=your_key
```

---

## Project Roadmap

### Phase 1 — Core RAG System ✅

* [x] ChromaDB Integration
* [x] Embeddings Pipeline
* [x] LangChain Retrieval
* [x] Groq Integration
* [x] Knowledge-Based Responses

### Phase 2 — WhatsApp Integration 🚧

* [x] Meta Developer Setup
* [x] WhatsApp Business Platform Setup
* [x] Access Token Configuration
* [x] Webhook Setup
* [x] Message Receiving
* [ ] Auto Reply System

### Phase 3 — Business Knowledge Management

* [ ] PDF Upload Support
* [ ] DOCX Upload Support
* [ ] Knowledge Base Updates
* [ ] Multi-Document Retrieval

### Phase 4 — Voice Intelligence

* [ ] Voice Note Processing
* [ ] Speech-to-Text
* [ ] Sarvam Voice Responses
* [ ] End-to-End Voice Conversations

### Phase 5 — SaaS Platform

* [ ] Multi-Business Support
* [ ] Admin Dashboard
* [ ] Analytics & Insights
* [ ] Subscription Plans

---

## Current Status

### AI Layer

80% Complete

### WhatsApp Infrastructure

70% Complete

### End-to-End Product

60% Complete

Current Focus:
**Webhook Integration → WhatsApp Messaging → RAG Connection**

---

## Future Vision

A business owner uploads documents once.

Customers ask questions through WhatsApp.

Bharat Voice AI automatically retrieves business information, generates contextual responses, and assists customers 24/7.

---

## Author

**Harsh Alreja**

Building practical AI products for Indian businesses using RAG, Vector Databases, LLMs, and Conversational AI.

GitHub: https://github.com/HarshAlreja

LinkedIn: https://www.linkedin.com/in/harsh-alrejaa
