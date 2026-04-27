import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.chat_models import ChatZhipuAI
# 🌟 核心組件：用於串聯檢索與問答的工廠函數
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()
api_key = os.getenv("ZHIPUAI_API_KEY")

# 1. 喚醒昨天的組件
print("⏳ 1. 初始化本地向量大腦與資料庫...")
embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
vectorstore = Chroma(persist_directory="./my_chroma_db", embedding_function=embeddings)

# 2. 初始化 AI 大腦 (智譜 GLM-4)
llm = ChatZhipuAI(model="glm-4-flash", api_key=api_key, temperature=0.1)

# 3. 設計「給 AI 的專屬指令」(Prompt)
# 我們必須告訴 AI：這是一些參考資料，請根據這些資料來回答。
system_prompt = (
    "你是一個專業的助理。請根據以下提供的「檢索內容」來回答使用者的問題。"
    "如果你在內容中找不到答案，請老實說你不知道，不要胡編亂造。"
    "\n\n"
    "{context}"
)

prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    ("user", "{input}"),
])

# 4. 構建「合體鏈」
# A. 負責把找出來的文件「塞」進 Prompt 裡的組件
question_answer_chain = create_stuff_documents_chain(llm, prompt_template)

# B. 完整的檢索鏈：結合了 向量資料庫檢索器 (Retriever) + 問答組件
retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
rag_chain = create_retrieval_chain(retriever, question_answer_chain)

# ==========================================
# 5. 終極測試：一鍵問答
# ==========================================
user_query = "這週的 Day 18 任務是什麼？"
print(f"\n🙋‍♂️ 提問：{user_query}")
print("🚀 RAG 鏈條運作中...")

# 執行！這一步包含了檢索、填充與生成
response = rag_chain.invoke({"input": user_query})

print("\n🤖 AI 的精準回答：")
print("-" * 30)
print(response["answer"])
print("-" * 30)

# 🔍 驗證：AI 到底是參考了哪幾段話？
print("\n📚 參考來源：")
for i, doc in enumerate(response["context"]):
    print(f"[{i+1}] {doc.page_content[:50]}...")