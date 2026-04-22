from langchain_community.document_loaders import TextLoader, PyPDFLoader

# ==========================================
# 1. 讀取 TXT 文字檔
# ==========================================
def load_txt():
    print("📖 正在載入 TXT 檔案...")
    loader = TextLoader("test.txt", encoding="utf-8")
    # load() 會回傳一個清單，裡面包含 Document 物件
    docs = loader.load()
    
    # 印出第一份文件的內容
    print(f"內容節錄：{docs[0].page_content[:50]}...")
    print(f"元數據：{docs[0].metadata}")
    return docs

# ==========================================
# 2. 讀取 PDF 檔案 (支援分頁)
# ==========================================
def load_pdf():
    print("\n📄 正在載入 PDF 檔案...")
    loader = PyPDFLoader("test.pdf")
    # PDF Loader 通常會按「頁」拆分，每一頁都是一個 Document 物件
    pages = loader.load()
    
    print(f"總頁數：{len(pages)}")
    # 查看第一頁
    print(f"第一頁內容節錄：{pages[0].page_content[:50]}...")
    print(f"第一頁元數據：{pages[0].metadata}")
    return pages

if __name__ == "__main__":
    # 測試執行
    txt_docs = load_txt()
    pdf_pages = load_pdf()