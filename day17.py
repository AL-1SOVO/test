# 🌟 1. 換成 TextLoader
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

print("📖 1. 正在載入 TXT 中...")
# 🌟 2. 載入我們確定有內容的 test.txt (記得加 encoding!)
loader = TextLoader("test.txt", encoding="utf-8")
pages = loader.load()

# ================= 以下代碼完全不變 =================
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=150,      # 為了讓 txt 也能切出很多塊，我們把 size 調小一點，設定 150 字
    chunk_overlap=30,    # 重疊 30 字
    separators=["\n\n", "\n", "。", "！", "？", "，", " ", ""] 
)

print("🔪 2. 開始執行智能切割...")
chunks = text_splitter.split_documents(pages)

print(f"✅ 3. 切割完成！被切成了 {len(chunks)} 個資料塊 (Chunks)。\n")
print("=" * 50)

# 抽查前三個區塊
for i in range(min(3, len(chunks))):
    print(f"📦 【區塊 {i+1}】")
    print(f"字數：{len(chunks[i].page_content)} 字")
    print(f"內容：{chunks[i].page_content}")
    print("-" * 50)