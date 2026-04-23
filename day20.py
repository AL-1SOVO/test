import os
# 🌟 必備組件：本地開源大腦與 Chroma 資料庫
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_chroma import Chroma

print("⏳ 1. 正在喚醒本地向量化引擎...")
# ⚠️ 注意：必須用跟昨天存檔時一模一樣的模型，否則座標會對不上！
embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

print("🗄️ 2. 正在連接本地的 Chroma 知識圖書館...")
# 指定我們昨天建立的那個資料夾
persist_directory = "./my_chroma_db"

# 直接連接資料庫 (不重新存入，只負責讀取)
vectorstore = Chroma(
    persist_directory=persist_directory,
    embedding_function=embeddings
)

# ==========================================
# 3. 終極測試：發起相似度檢索 (Similarity Search)
# ==========================================
# 👇 這裡可以換成你想問的任何問題！根據你 test.txt 的內容來問
query = "這週會學到什麼開發框架？" 
print(f"\n🙋‍♂️ 你的問題：『{query}』")
print("🔍 AI 正在圖書館中翻找最相關的文獻...")

# 執行相似度檢索，k=3 代表我們只要「最接近的前 3 個結果」
results = vectorstore.similarity_search(query, k=3)

print("\n🎉 檢索完成！為你找到以下 3 段最相關的原文：\n")
print("=" * 50)

# 4. 把找出來的結果印出來看看
for i, doc in enumerate(results):
    print(f"🥇 【第 {i+1} 名相關文獻】")
    print(f"📖 內容：{doc.page_content}")
    # 看看它是不是連來源的 Metadata 都完整記得了！
    print(f"🏷️ 來源標籤：{doc.metadata}")
    print("-" * 50)