import os
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_community.chat_models import ChatZhipuAI

# 載入環境變數 (API Key)
load_dotenv()
api_key = os.getenv("ZHIPUAI_API_KEY")

print("⏳ 1. 正在連接本地圖書館與 AI 大腦...")
embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
vectorstore = Chroma(persist_directory="./my_chroma_db", embedding_function=embeddings)
llm = ChatZhipuAI(model="glm-4-flash", api_key=api_key, temperature=0.1)

# 你可以隨意修改這個問題，來測試 PDF 裡的其他內容
user_query = "這堂課推薦使用什麼向量大腦？"
print(f"\n🙋‍♂️ 提問：{user_query}")

# ==========================================
# 🌟 檢索並提取 Metadata (來源與頁碼)
# ==========================================
results = vectorstore.similarity_search(user_query, k=3)

context_text = ""
sources_list = [] # 準備一個空列表，用來收集「來源身分證」

for i, doc in enumerate(results):
    # 1. 組合給 AI 看的純文字小抄
    context_text += f"[參考段落 {i+1}]: {doc.page_content}\n"
    
    # 2. 提取 Metadata 來源資訊！
    source_file = doc.metadata.get('source', '未知來源')
    
    # 🌟 處理頁碼：讓 0 變成 第 1 頁
    page_num = doc.metadata.get('page')
    if isinstance(page_num, int):
        page_display = f"第 {page_num + 1} 頁"
    else:
        page_display = "無頁碼"
    
    # 把這段資料的來源記錄下來
    source_info = f"來源檔案: {source_file} | 頁面: {page_display}"
    sources_list.append(f"[參考段落 {i+1}] {source_info}")

# ==========================================
# 🌟 組合 Prompt 並生成回答
# ==========================================
prompt = f"""你是一個專業的助理。請根據以下「參考資料」回答問題。
在回答的最後，不需你自己加上來源，我會在程式中自動幫你補上。
如果你在資料中找不到答案，請老實說不知道。

【參考資料】
{context_text}

【問題】
{user_query}
"""

response = llm.invoke(prompt)

# ==========================================
# 🌟 終極輸出：結合 AI 回答 + 確鑿證據
# ==========================================
print("\n🤖 AI 的精準回答：")
print("=" * 50)
print(response.content)
print("\n" + "-" * 50)
print("📌 【參考來源追蹤】")
# 用 set() 過濾掉重複的來源，然後一行一行印出來
for source in set(sources_list): 
    print(source)
print("=" * 50)