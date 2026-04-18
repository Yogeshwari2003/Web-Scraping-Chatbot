Web-Scraping-Chatbot
An AI-powered chatbot backend built with Flask that combines LLaMA 3.3 (via Groq), real-time web search (SerpAPI), and live website scraping (Playwright + BeautifulSoup) to deliver accurate, up-to-date answers.

🚀 Features

 LLM-Powered – Uses LLaMA 3.3 70B via Groq for fast, intelligent responses
 Real-Time Web Search – Integrates SerpAPI to fetch live search results
 Website Scraping – Scrapes and parses live web pages from URLs shared in chat
 Multi-Session Support – Maintains separate conversation history per user via unique session IDs
 Chat History Saving – Automatically saves each session as a JSON file
 Dual Interface – Accessible via REST API (Flask) or CLI terminal chat


🛠️ Tech Stack
Backend => Python, Flask
LLM => LLaMA 3.3 70B (Groq API)SearchSerpAPI + LangChain
Scraping => Playwright, BeautifulSoup4

⚙️ Setup & Installation

1. Clone the repository
git clone https://github.com/Yogeshwari2003/Web-Scraping-Chatbot.git
cd Web-Scraping-Chatbot

3. Install dependencies
pip install -r requirements.txt

4. Install Playwright browser
playwright install chromium

5. Create a .env file
GROQ_API_KEY=your_groq_api_key_here
SERPAPI_API_KEY=your_serpapi_key_here

▶️ Run the App
API Server (Flask):
python app.py
CLI Chat Mode:
python main.py
