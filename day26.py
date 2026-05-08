import streamlit as st

# 1. 設定網頁標籤頁的標題與 Icon
st.set_page_config(page_title="我的專屬 AI 助理", page_icon="🤖")

# 2. 頁面的大標題與文字說明
st.title("🤖 歡迎來到你的 AI 網頁助理")
st.write("太感動了！這是我們告別黑底白字，邁向網頁界面的第一步！🎉")

# 畫一條分隔線
st.divider()

# 3. 建立一個對話輸入框
user_input = st.text_input("請輸入你想對 AI 說的話：", placeholder="例如：你好呀！")

# 4. 建立一個「送出」按鈕
# 當按鈕被點擊時，st.button 會變成 True，就會執行下面的程式碼
if st.button("送出問題", type="primary"):
    
    if user_input:
        # 如果使用者有輸入文字，顯示成功訊息
        st.success(f"網頁已成功收到你的訊息：【{user_input}】")
        st.info("💡 提示：今天我們先做 UI 介面，明天我們就會把智譜大腦和 ChromaDB 接上來！")
    else:
        # 如果使用者什麼都沒打就按送出，顯示警告訊息
        st.warning("請先輸入文字再按送出喔！")