# 🚀 Web-Scraping Service  

## 📌 Overview

**AgentFlow For Web-Scrap** is a high-concurrency, asynchronous **FastAPI** service that implements a **Universal Web-Intelligence Agent** For Fetch infromtion from provided website URL and Answer The Question.

Unlike standard **RAG systems** that rely on static databases, this service utilizes a **ReAct (Reason + Act) Agent** to scrape and analyze any live website URL in real-time.

Built with **LangGraph** and **Groq **, it is designed to be **cost-effective**, using free-tier resources while maintaining **production-grade logic and observability**.

---

# 🏗 Project Structure

```bash
chatbot-service/
├── app/
│   ├── api/
│   │   └── routes.py      # FastAPI endpoints and route handlers
│   ├── services/
│   │   └── chatbot.py     # LangGraph Orchestrator & Tool definitions
│   ├── schemas/
│   │   └── chat.py        # Pydantic v2 Models (Strict Validation)
│   ├── core/
│   │   └── prompts.py     # Universal Search Persona & System Instructions
│   ├── utils/
│   │   └── helpers.py     # Web scraping & Text cleaning utilities
│   └── main.py            # FastAPI Entry Point
├── .env                   # API Keys & Configuration (GIT IGNORED)
└── requirements.txt       # Production Dependencies
```

---

# 🧠 How the Agentic Flow Works

The service follows a **dynamic ReAct loop** using **LangGraph** to ensure **zero-hallucination responses**.

### Step-by-Step Flow

1. **Input**

   * User provides:

     * `message`
     * optional `url`

2. **Reasoning — (Node: Agent)**

   * The LLM (**Groq**) analyzes the intent.
   * If a URL is present, it triggers:

     ```
     fetch_website_content
     ```

3. **Action — (Node: Tools)**

   * The scraper:

     * Fetches HTML
     * Removes scripts/styles
     * Cleans noise
     * Returns the **top 8,000 characters**

4. **Observation**

   * The Agent receives the live text.
   * Generates answers **strictly grounded in context**.

5. **Output**

   * Returns a **validated JSON response**.

---

# 🛠 Installation & Setup

## 1️⃣ Clone the Repository

```bash
git clone <repo-link>
cd chatbot-service-agentic
```

---

## 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

**Windows**

```bash
venv\Scripts\activate
```

**macOS / Linux**

```bash
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 4️⃣ Configure Environment Variables

Create a `.env` file:

```env
GROQ_API_KEY=your_groq_api_key_here
PORT=8000
```

---

## 5️⃣ Run the Server

```bash
uvicorn app.main:app --reload
```

API Documentation will be available at:

```text
http://127.0.0.1:8000/docs
```

---

# 📡 Example API Request

```json
{
  "message": "What are the latest services offered?",
  "url": "https://malindtech.com/",
  "history": []
}
```

---

# 📜 Example Logs

```text
🤖 [AGENT LOG] Initiating reasoning loop...

🔍 [AGENT LOG] Scraping: https://malindtech.com/

✅ [SUCCESS] Returning grounded response based on live site data.
```

---

# ⚙️ Key Features

* ⚡ Async FastAPI architecture
* 🧠 LangGraph ReAct Agent workflow
* 🌐 Real-time website scraping
* 📦 Strict Pydantic v2 validation
* 🔒 Environment-based configuration
* 📊 Production-ready logging
* 💰 Optimized for free-tier usage

---

# 🧩 Tech Stack

* **FastAPI**
* **LangGraph**
* **Groq Api**
* **Pydantic v2**
* **Python 3.10+**
* **AsyncIO**
* **BeautifulSoup**
* **HTTPX**

---

# 🔐 Environment & Security Notes

* `.env` file **must be git-ignored**
* Never commit API keys
* Use environment variables in production
* Add `.env` to `.gitignore`:

```bash
.env
venv/
__pycache__/
*.pyc
```

---

# 📌 Future Improvements

* Redis caching layer
* Rate limiting middleware
* Streaming responses
* Observability dashboards
* Multi-URL reasoning support
* Persistent conversation memory

---

# 👨‍💻 Author

**Malindatech**

Production-ready **Agentic AI Infrastructure** ⚡

---

# Deploy Architecture (Recommended)

- Backend API: Railway
- Frontend UI: Vercel
- WordPress: Embed Vercel URL in an iframe

---

# Deploy Backend on Railway

This repository is pre-configured for Railway with `Procfile` and `railway.toml`.

## Required Railway Environment Variables

- `GROQ_API_KEY` = your Groq API key
- `CORS_ORIGINS` = comma-separated allowed origins (include your Vercel domain and WordPress domain)

Example:

```text
CORS_ORIGINS=https://your-frontend.vercel.app,https://your-wordpress-domain.com
```

## Railway Steps

1. Create a Railway project and connect this repository.
2. Railway installs dependencies from `requirements.txt`.
3. Add `GROQ_API_KEY` and `CORS_ORIGINS` in Railway Variables.
4. Deploy.

Backend health endpoint:

```text
https://<your-railway-domain>/health
```

Backend chat endpoint:

```text
https://<your-railway-domain>/api/v1/chat
```

---

# Deploy Frontend on Vercel

This repository is configured to serve static frontend from `app/static/index.html`.

## Vercel Steps

1. Create a Vercel project from this repository.
2. Deploy (no Python runtime needed on Vercel for this setup).
3. Open your frontend URL.

To connect frontend to Railway backend, append `api_base` query parameter:

```text
https://<your-vercel-domain>/?api_base=https://<your-railway-domain>/api/v1
```

---

# WordPress iFrame Integration

Give this iframe snippet to your web developer (replace domains):

```html
<iframe
   src="https://<your-vercel-domain>/?api_base=https://<your-railway-domain>/api/v1"
   width="100%"
   height="700"
   style="border:0; border-radius:12px;"
   loading="lazy"
   referrerpolicy="strict-origin-when-cross-origin"
   allow="microphone">
</iframe>
```
