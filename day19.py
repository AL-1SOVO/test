import os
# 🌟 修改點 1：將 TextLoader 換成 PyPDFLoader
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_chroma import Chroma

# ==========================================
# 1. 讀取與切塊 (升級為 PDF 版)
# ==========================================
print("📖 1. 正在載入並切割 PDF 文件...")

# 🌟 修改點 2：改用 PyPDFLoader 並指定你的 test.pdf
loader = PyPDFLoader("test.pdf")
pages = loader.load()

# 這裡不變，PDF 載入後也會被切成一小塊一小塊
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=150, 
    chunk_overlap=30,
    separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""]
)
chunks = text_splitter.split_documents(pages)
print(f"✅ 成功從 PDF 中切出 {len(chunks)} 個文字區塊！")

# ==========================================
# 2. 初始化向量化大腦 (維持不變)
# ==========================================
print("\n🧠 2. 正在啟動本地向量化引擎...")
embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

# ==========================================
# 3. 存入 ChromaDB (會自動包含頁碼資訊)
# ==========================================
print("\n🗄️ 3. 正在將 PDF 內容與座標存入 ChromaDB...")

persist_directory = "./my_chroma_db"

vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=persist_directory
)

print(f"\n🎉 任務完成！你的 PDF 知識庫已建立。")
print(f"現在執行 Day 25 的程式碼，你就能看到真實的頁碼來源了！")