import streamlit as st
import requests

# 配置
API_URL = "http://127.0.0.1:8000/chat_stream"
st.set_page_config(page_title="智慧大棚 AI 中控", page_icon="🌱")
st.title("🌱 智慧大棚 5G 助理")

avatars = {"user": "🧑‍🌾", "assistant": "🤖"}

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "您好！流式打字機功能已上線，快來試試看！"}]

# 渲染歷史
for msg in st.session_state.messages:
    with st.chat_message(msg["role"], avatar=avatars.get(msg["role"])):
        st.markdown(msg["content"])

# 處理輸入
if prompt := st.chat_input("請輸入指令..."):
    with st.chat_message("user", avatar=avatars["user"]):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant", avatar=avatars["assistant"]):
        # 🌟 定義流式接收生成器
        def stream_data():
            # 開啟 stream=True 模式
            with requests.post(API_URL, data={"message": prompt}, stream=True) as r:
                for chunk in r.iter_content(chunk_size=None, decode_unicode=True):
                    if chunk:
                        yield chunk

        # 🌟 呼叫 Streamlit 內建的流式顯示函數
        full_response = st.write_stream(stream_data())
        st.session_state.messages.append({"role": "assistant", "content": full_response})