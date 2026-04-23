import os
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_chroma import Chroma  # 🌟 今天的全新積木：Chroma 資料庫

# ==========================================
# 1. 讀取與切塊 (Day 17 的成果)
# ==========================================
print("📖 1. 正在載入並切割 TXT 文件...")
# 備註：我們繼續用 test.txt 來確保一定有文字可以切！
loader = TextLoader("test.txt", encoding="utf-8")
pages = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=150, 
    chunk_overlap=30,
    separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""]
)
chunks = text_splitter.split_documents(pages)
print(f"✅ 成功切出 {len(chunks)} 個文字區塊！")

# ==========================================
# 2. 初始化向量化大腦 (Day 18 的成果)
# ==========================================
print("\n🧠 2. 正在啟動本地向量化引擎...")
# 使用我們昨天成功跑起來的免費開源大腦
embeddings = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-zh-v1.5")

# ==========================================
# 3. 存入 ChromaDB (Day 19 的終極任務)
# ==========================================
print("\n🗄️ 3. 正在將文字與座標存入 ChromaDB 向量資料庫...")

# 定義資料庫要存在你電腦裡的哪個資料夾
persist_directory = "./my_chroma_db"

# 🚀 開始施展魔法：把 chunks 和 embeddings 交給 Chroma 處理
# 這一步會把文字轉成數字，並永久儲存到你的硬碟裡！
vectorstore = Chroma.from_documents(
    documents=chunks,
    embedding=embeddings,
    persist_directory=persist_directory
)

print(f"\n🎉 任務完成！你的專屬 AI 圖書館已經建立。")
print(f"👉 請打開 VSCode 左側的檔案總管，你應該會看到一個多出來的資料夾叫做：{persist_directory}")