import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.chat_models import ChatZhipuAI

load_dotenv()
api_key = os.getenv("ZHIPUAI_API_KEY")

print("⏳ 1. 初始化本地大腦與資料庫...")
embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
vectorstore = Chroma(persist_directory="./my_chroma_db", embedding_function=embeddings)
llm = ChatZhipuAI(model="glm-4-flash", api_key=api_key, temperature=0.1)

# 🛑 故意問一個來亂的問題！
user_query = "這堂課會教怎麼文本分割嗎？"
print(f"\n🙋‍♂️ 提問：{user_query}")

# ==========================================
# 🌟 檢索優化：帶分數檢索與及格門檻
# ==========================================
print("🔍 進行精準檢索 (設定最大 Top-K = 9)...")

# 使用 _with_relevance_scores 方法，這會同時回傳「資料」與「相似度分數 (0~1)」
raw_results = vectorstore.similarity_search_with_relevance_scores(user_query, k=5)

# 🎯 設定你的 Threshold (及格門檻)，通常 0.5 ~ 0.7 之間是個好起點
SCORE_THRESHOLD = 0.5 
valid_docs = []

print("\n📊 檢索分數過濾報告：")
for i, (doc, score) in enumerate(raw_results):
    # 判斷有沒有及格
    if score >= SCORE_THRESHOLD:
        status = "✅ 及格錄取"
        valid_docs.append(doc)
    else:
        status = "❌ 分數太低淘汰"
        
    print(f"片段 {i+1} | 分數: {score:.4f} | {status} | 內容: {doc.page_content[:15]}...")

# ==========================================
# 🌟 組合 Context 與生成
# ==========================================
context_text = ""

# 只有在「有及格的資料」時，才拼湊小抄
if len(valid_docs) > 0:
    for i, doc in enumerate(valid_docs):
        context_text += f"[參考段落 {i+1}]: {doc.page_content}\n"
else:
    # 如果全軍覆沒，就給 AI 一張白紙
    context_text = "沒有找到任何相關的參考資料。"
    print("\n⚠️ 警告：沒有任何資料通過分數門檻，將不提供參考資料給 AI。")

prompt = f"""你是一個專業的助理。請嚴格根據以下「參考資料」來回答使用者的問題。
如果你在資料中找不到答案，或者參考資料為空，請老實說「抱歉，我的知識庫中沒有相關資訊」，絕對不可以胡編亂造。

【參考資料】
{context_text}

【使用者問題】
{user_query}
"""

response = llm.invoke(prompt)

print("\n🤖 AI 的精準回答：")
print("-" * 40)
print(response.content)
print("-" * 40)