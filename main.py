import os
import re
import uuid
import time
import json
import random
from datetime import datetime
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_community.utilities import SerpAPIWrapper
from playwright.sync_api import sync_playwright, TimeoutError
from bs4 import BeautifulSoup

# ================== CONFIG ==================
load_dotenv()
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SERPAPI_API_KEY = os.getenv("SERPAPI_API_KEY")

if not GROQ_API_KEY or not SERPAPI_API_KEY:
    raise EnvironmentError("❌ Set GROQ_API_KEY and SERPAPI_API_KEY in .env file.")

llm = ChatGroq(model="llama-3.3-70b-versatile", api_key=GROQ_API_KEY)
search_tool = SerpAPIWrapper()

chats = {}
CHAT_DIR = "chat_sessions"
os.makedirs(CHAT_DIR, exist_ok=True)

# ================== HELPERS ==================
def clean_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, "html.parser")
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav"]):
        tag.extract()
    text = soup.get_text(separator="\n")
    return re.sub(r"\s+", " ", text).strip()

def clean_llm_response(text: str) -> str:
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"[*•#]", "", text)
    text = re.sub(r"\n\s+", "\n", text)
    text = re.sub(r"\n{2,}", "\n\n", text)
    return text.strip()

def scrape_website_real_time(url: str, selector: str = None) -> str:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.set_extra_http_headers({"User-Agent": "Mozilla/5.0"})
        page.goto(url, wait_until="networkidle")
        time.sleep(3)
        content = ""
        try:
            if selector:
                page.wait_for_selector(selector, timeout=7000)
                elem = page.query_selector(selector)
                content = elem.inner_text() if elem else f"❌ Element not found: {selector}"
            else:
                content = page.content()
        except TimeoutError:
            content = f"❌ Timeout for selector: {selector}"
        except Exception as e:
            content = f"❌ Scraping failed: {str(e)}"
        browser.close()
    return clean_html(content) if not selector else content.strip()

# ================== QUERY TYPE ==================
def detect_query_type(user_text: str) -> str:
    greetings = ["hi", "hello", "hey", "how are you", "good morning", "good evening", "happy to meet you"]
    if any(greet in user_text.lower() for greet in greetings):
        return "greeting"
    return "factual"

def greeting_response() -> str:
    replies = [
        "I'm doing well, thanks for asking! How are you today?",
        "Happy to meet you! I'm doing great. How are you?",
        "I'm fine and excited to chat with you. How's your day going?",
        "Doing great! Thanks for asking. How about you?"
    ]
    return random.choice(replies)

# ================== ASSISTANT ==================
def ask_assistant(session_id: str, user_text: str) -> str:
    if session_id not in chats:
        chats[session_id] = [
            SystemMessage(content="You are a helpful assistant. Respond professionally, clearly, and warmly.")
        ]

    query_type = detect_query_type(user_text)
    scraped_data = ""
    answer = ""

    if query_type == "greeting":
        answer = greeting_response()

    elif query_type == "factual":
        urls = re.findall(r"(https?://[^\s]+)", user_text)
        for url in urls:
            scraped_data += f"\n\n🔎 Real-Time Scraped Content ({url}):\n{scrape_website_real_time(url)}"

        search_results = search_tool.run(user_text)
        full_message = f"User question: {user_text}\n\nSearch Results:\n{search_results}\n{scraped_data}"
        chats[session_id].append(HumanMessage(content=full_message))
        llm_response = llm.invoke(chats[session_id])
        answer = clean_llm_response(llm_response.content)

    else:  # advice / reasoning
        chats[session_id].append(HumanMessage(content=user_text))
        llm_response = llm.invoke(chats[session_id])
        answer = clean_llm_response(llm_response.content)

    chats[session_id].append(AIMessage(content=answer))

    # Save chat session to JSON
    session_file = os.path.join(CHAT_DIR, f"{session_id}.json")
    with open(session_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "session_id": session_id,
                "timestamp": datetime.now().isoformat(),
                "chat_history": [msg.content for msg in chats[session_id]]
            },
            f,
            indent=4,
            ensure_ascii=False
        )

    return answer

# ================== CLI CHAT ==================
def run_chat():
    session_id = str(uuid.uuid4())
    print(f"\n💬 New Chat Started (Session: {session_id})")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ["exit", "quit", "bye"]:
            # FORCE SAVE BEFORE EXIT
            session_file = os.path.join(CHAT_DIR, f"{session_id}.json")
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "session_id": session_id,
                        "timestamp": datetime.now().isoformat(),
                        "chat_history": [
                            {
                                "role": msg.__class__.__name__,
                                "content": msg.content
                            }
                            for msg in chats.get(session_id, [])
                        ]
                    },
                    f,
                    indent=4,
                    ensure_ascii=False
                )
            print(f"\nAssistant: Goodbye! Chat saved at:\n{session_file}")
            break

        answer = ask_assistant(session_id, user_input)
        print("\nAssistant:\n", answer, "\n")


# ================== RUN ==================
if __name__ == "__main__":
    run_chat()
