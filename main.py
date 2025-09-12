import os
import re
import uuid
from dotenv import load_dotenv
from langchain_groq import ChatGroq  
from langchain.schema import HumanMessage, AIMessage, SystemMessage 
from langchain_community.utilities import SerpAPIWrapper
from playwright.sync_api import sync_playwright 
from bs4 import BeautifulSoup 

# ================== CONFIG ==================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

if not GROQ_API_KEY or not SERPAPI_API_KEY:
    raise EnvironmentError("❌ Set GROQ_API_KEY and SERPAPI_API_KEY in .env file.")

llm = ChatGroq(model="deepseek-r1-distill-llama-70b", api_key=GROQ_API_KEY)
search_tool = SerpAPIWrapper()

# In-memory store for chats
chats = {}

# ================== HELPERS ==================
def clean_html(html_content: str) -> str:
    """Clean HTML -> readable text."""
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.extract()
    text = soup.get_text(separator="\n")
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[*•#]", "", text)
    return text.strip()

def clean_llm_response(text: str) -> str:
    """Format Groq LLM response for readability."""
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"[*•#]", "", text)
    text = re.sub(r"\n\s+", "\n", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip()

def scrape_website(url: str) -> str:
    """Scrape and clean website content using Playwright."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url)
        content = page.content()
        browser.close()
    return clean_html(content)

# ================== ASSISTANT ==================
def ask_assistant(session_id: str, user_text: str) -> str:
    if session_id not in chats:
        chats[session_id] = [
            SystemMessage(content="You are a helpful assistant. Use past chat context to stay consistent.")
        ]

    # Run web search
    print(f"[🔍] Searching: {user_text}")
    search_results = search_tool.run(user_text)

    if "example.com" in user_text.lower():
        site_content = scrape_website("https://example.com")
        search_results += f"\n\n🔎 Site Scraped Content (cleaned):\n{site_content}"

    # Add latest user message with search results included
    chats[session_id].append(
        HumanMessage(content=f"{user_text}\n\n[Search Results]:\n{search_results}")
    )

    # Call LLM with structured messages (history preserved)
    llm_response = llm.invoke(chats[session_id])

    # Clean response
    cleaned_response = clean_llm_response(llm_response.content)

    # Save assistant reply into memory
    chats[session_id].append(AIMessage(content=cleaned_response))

    return cleaned_response

# ================== MAIN CHAT ==================
def run_chat():
    session_id = str(uuid.uuid4())  # unique chat session
    print(f"\n\n💬 New Chat Started (Session: {session_id})")
    print("Hi, I am a Web Search Chatbot. Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("Chatbot: Goodbye! (Your chat is kept in memory 🧠)")
            break
        answer = ask_assistant(session_id, user_input)
        print("\nAssistant:\n", answer, "\n\n")

# ================== FLASK INTEGRATION ==================

