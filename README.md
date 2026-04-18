# Web-Scraping-Chatbot

A powerful AI chatbot backend built with Flask that combines large language models, real-time web search, and live website scraping to deliver accurate, up-to-date answers to user queries.

🚀 Features

LLM-Powered – Uses LLaMA 3.3 70B via Groq for fast, intelligent, and context-aware responses

Real-Time Web Search – Integrates SerpAPI to fetch live search results for factual queries

Website Scraping – Uses Playwright + BeautifulSoup to scrape and parse live web pages from URLs shared in chat

Multi-Session Support – Maintains separate conversation history per user using unique session IDs

Chat History Saving – Automatically saves each session as a JSON file for future reference

Dual Interface – Accessible via REST API (Flask) or directly through a CLI terminal chat

🛠️ Tech Stack
Backend => Python, Flask

LLM => LLaMA 3.3 70B (Groq API)SearchSerpAPI + LangChain

Scraping => Playwright, BeautifulSoup4

Setup & Installation

1. Clone the repository
git clone https://github.com/Yogeshwari2003/Web-Scraping-Chatbot.git
cd Web-Scraping-Chatbot

2. Install dependencies
pip install -r requirements.txt

3. Install Playwright browser
playwright install chromium

4. Create a .env file
GROQ_API_KEY=your_groq_api_key_here

SERPAPI_API_KEY=your_serpapi_key_here

▶️ Run the App

Run the API server: python app.py

Run CLI chat: python main.py
