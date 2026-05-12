import streamlit as st
import requests

API_URL = "http://127.0.0.1:8000/chat_stream"
st.set_page_config(page_title="智慧大棚 AI 中控", page_icon="🌱", layout="wide")

# ==========================================
# 1. 側邊欄 (掛載檔案)
# ==========================================
with st.sidebar:
    st.header("📎 數據分析中心")
    # 建立上傳器
    uploaded_file = st.file_uploader("上傳大棚歷史數據 (CSV)", type=["csv"])
    
    if uploaded_file:
        st.success(f"✅ 已掛載文件：{uploaded_file.name}")
        
    st.markdown("---")
    if st.button("🗑️ 清空歷史對話", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

st.title("🌱 智慧大棚 5G 助理 (多模態版)")

# 初始化保險箱
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "您好！請在左側上傳 CSV 檔案，然後問我問題吧！"}]

avatars = {"user": "🧑‍🌾", "assistant": "🤖"}

# 渲染歷史紀錄
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=avatars.get(msg["role"])):
        st.markdown(msg["content"])

# ==========================================
# 2. 處理發送與檔案打包 (🌟 今天的核心)
# ==========================================
if prompt := st.chat_input("請幫我分析這份數據..."):
    with st.chat_message("user", avatar=avatars["user"]):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=avatars["assistant"]):
        def stream_data():
            try:
                # 🌟 第一步：準備包裹！如果左側有檔案，就把它打包成 HTTP 格式
                files_payload = None
                if uploaded_file is not None:
                    files_payload = {
                        # 格式: ("檔名", 檔案的二進位內容, "檔案類型")
                        "file": (uploaded_file.name, uploaded_file.getvalue(), "text/csv")
                    }
                
                # 🌟 第二步：交給郵差！把 data(文字) 和 files(檔案) 一起發送給 FastAPI
                with requests.post(API_URL, data={"message": prompt}, files=files_payload, stream=True) as r:
                    r.raise_for_status()
                    for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                        if chunk:
                            yield chunk
            except Exception as e:
                yield f"❌ 網路錯誤：{e}"

        # 接收流式結果並存入保險箱
        full_response = st.write_stream(stream_data())
        st.session_state.messages.append({"role": "assistant", "content": full_response})