# test_gemini_connection.py
from dotenv import load_dotenv
load_dotenv()

from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-3.6-flash", temperature=0)
response = llm.invoke("Balas dengan satu kata: OK")
print(response.content)
