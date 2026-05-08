import os
import tempfile
import streamlit as st
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.embeddings import HuggingFaceBgeEmbeddings
from langchain_chroma import Chroma
from langchain_community.chat_models import ChatZhipuAI

# 1. 網頁基本設定
st.set_page_config(page_title="Chat-Your-PDF 助手", page_icon="📚", layout="wide")
load_dotenv()
api_key = os.getenv("ZHIPUAI_API_KEY")

# 2. 載入模型 (使用快取，避免每次網頁重整都重新下載模型)
@st.cache_resource
def load_ai_models():
    embed_model = HuggingFaceBgeEmbeddings(model_name="BAAI/bge-small-zh-v1.5")
    chat_model = ChatZhipuAI(model="glm-4-flash", api_key=api_key, temperature=0.1)
    return embed_model, chat_model

embeddings, llm = load_ai_models()

# 3. 初始化網頁記憶體 (Session State)
if "messages" not in st.session_state:
    st.session_state.messages = [] # 儲存聊天紀錄
if "vectorstore" not in st.session_state:
    st.session_state.vectorstore = None # 儲存資料庫

# ==========================================
# 🌟 左側邊欄：處理 PDF 上傳與向量化
# ==========================================
with st.sidebar:
    st.header("📂 上傳你的文件")
    uploaded_file = st.file_uploader("請上傳 PDF 檔案", type="pdf")
    
    if st.button("處理文件 🚀", type="primary"):
        if uploaded_file is not None:
            with st.spinner("正在閱讀並理解文件中，請稍候..."):
                # 將上傳的檔案暫存到電腦裡
                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_file_path = tmp_file.name
                
                # 執行我們熟悉的 Day 19 流程：讀取、切塊、存入資料庫
                loader = PyPDFLoader(tmp_file_path)
                pages = loader.load()
                
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=300, chunk_overlap=50)
                chunks = text_splitter.split_documents(pages)
                
                # 建立暫時的 Chroma 資料庫 (存在網頁記憶體中)
                st.session_state.vectorstore = Chroma.from_documents(chunks, embeddings)
                
                st.success("文件處理完成！現在可以開始提問了。")
        else:
            st.warning("請先上傳 PDF 檔案喔！")

# ==========================================
# 🌟 主畫面：聊天介面與 RAG 檢索生成
# ==========================================
st.title("📚 Chat-Your-PDF 智能問答")
st.write("請先在左側上傳 PDF 文件，然後就可以在下方問我關於文件的問題囉！")

# 將歷史聊天紀錄畫在畫面上
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 接收使用者的輸入
if user_query := st.chat_input("請輸入你想查詢的內容..."):
    
    # 1. 把使用者的問題顯示在畫面上，並存入記憶
    with st.chat_message("user"):
        st.markdown(user_query)
    st.session_state.messages.append({"role": "user", "content": user_query})
    
    # 2. 檢查大腦是否準備好
    if st.session_state.vectorstore is None:
        with st.chat_message("assistant"):
            warning_msg = "⚠️ 哎呀！你還沒有上傳或處理 PDF 文件喔，請先在左邊上傳文件。"
            st.markdown(warning_msg)
            st.session_state.messages.append({"role": "assistant", "content": warning_msg})
    
    # 3. 執行 RAG 檢索與生成
    else:
        with st.chat_message("assistant"):
            # 顯示「正在思考...」的動畫
            with st.spinner("正在翻閱文件尋找答案..."):
                # 檢索資料 (Day 22)
                results = st.session_state.vectorstore.similarity_search(user_query, k=3)
                
                context_text = ""
                sources = []
                for i, doc in enumerate(results):
                    context_text += f"[參考段落 {i+1}]: {doc.page_content}\n"
                    page_num = doc.metadata.get('page', 0) + 1
                    sources.append(f"第 {page_num} 頁")
                
                # 組裝 Prompt
                prompt = f"""你是一個專業的助理。請嚴格根據以下「參考資料」回答問題。
                如果你在資料中找不到答案，請老實說不知道。
                
                【參考資料】
                {context_text}
                
                【問題】
                {user_query}
                """
                
                # 呼叫智譜 AI
                response = llm.invoke(prompt).content
                
                # 組合最後要顯示在網頁上的完整回答 (包含來源)
                final_reply = f"{response}\n\n---\n*📌 參考來源: {', '.join(set(sources))}*"
                
                # 顯示回答並存入記憶
                st.markdown(final_reply)
                st.session_state.messages.append({"role": "assistant", "content": final_reply})