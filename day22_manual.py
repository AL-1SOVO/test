import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.chat_models import ChatZhipuAI
# 🛑 徹底刪除了 langchain.chains 的依賴！

load_dotenv()
api_key = os.getenv("ZHIPUAI_API_KEY")

# 1. 喚醒大腦與資料庫
print("⏳ 1. 初始化本地向量大腦與資料庫...")
embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
vectorstore = Chroma(persist_directory="./my_chroma_db", embedding_function=embeddings)
llm = ChatZhipuAI(model="glm-4-flash", api_key=api_key, temperature=0.1)

user_query = "這週的 Day 18 任務是什麼？"
print(f"\n🙋‍♂️ 提問：{user_query}")
print("🚀 手動 RAG 流程運作中...")

# ==========================================
# 🌟 RAG 手動三步曲 (透明、穩定、不報錯！)
# ==========================================

# 【步驟 1：檢索】自己去圖書館找資料
results = vectorstore.similarity_search(user_query, k=3)

# 【步驟 2：組合】把找到的 3 段資料，組合成一段純文字
context_text = ""
for i, doc in enumerate(results):
    context_text += f"[參考段落 {i+1}]: {doc.page_content}\n"

# 【步驟 3：生成】寫一個清晰的 Prompt，把資料和問題一起塞給 AI
prompt = f"""你是一個專業的助理。請嚴格根據以下「參考資料」來回答使用者的問題。
如果你在資料中找不到答案，請老實說你不知道，絕對不可以胡編亂造。

【參考資料】
{context_text}

【使用者問題】
{user_query}
"""

# 執行對話！(直接把 prompt 丟給智譜 AI)
response = llm.invoke(prompt)

print("\n🤖 AI 的精準回答：")
print("-" * 40)
# response.content 就是 AI 吐出來的純文字回答
print(response.content)
print("-" * 40)

# 🔍 驗證區：讓你知道 AI 到底看了什麼
print("\n📚 剛才餵給 AI 的參考來源：")
print(context_text)