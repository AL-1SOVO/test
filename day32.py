import os
import random
import time
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage

# ==========================================
# 0. 基礎配置
# ==========================================
load_dotenv()
api_key = os.getenv("ZHIPUAI_API_KEY")
llm = ChatZhipuAI(model="glm-4-flash", api_key=api_key, temperature=0.1)

# ==========================================
# 🛠️ 1. 定義本地工具 (物理執行層)
# ==========================================
def get_sensor_data(location: str, sensor_type: str) -> str:
    print(f"\n   ⚙️ [底層執行] 正在連接 {location} 的 {sensor_type} 傳感器...")
    # 模擬讀取數據
    if sensor_type == "leaf_temperature":
        result = f"{round(random.uniform(20.0, 35.0), 1)}°C"
    else:
        result = "未知數據"
    print(f"   ✅ [底層執行完畢] 數據為: {result}")
    return result

# 工具說明書
get_sensor_data_schema = {
    "type": "function",
    "function": {
        "name": "get_sensor_data",
        "description": "獲取指定位置的農業物聯網傳感器數據。",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "位置，例如：大棚、一號車間"},
                "sensor_type": {"type": "string", "enum": ["leaf_temperature"], "description": "傳感器類型"}
            },
            "required": ["location", "sensor_type"]
        }
    }
}

llm_with_tools = llm.bind_tools([get_sensor_data_schema])

# ==========================================
# 🚀 2. FastAPI 伺服器
# ==========================================
app = FastAPI(title="農業智慧中控 Agent API")

# 【前端 UI】內建對話網頁
@app.get("/", response_class=HTMLResponse)
def chat_ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>智慧大棚 AI 助理</title>
        <meta charset="utf-8">
        <style>
            body { font-family: "Segoe UI", sans-serif; background-color: #eef2f3; margin: 0; display: flex; justify-content: center; align-items: center; height: 100vh; }
            .chat-container { width: 100%; max-width: 500px; height: 600px; background: white; border-radius: 20px; box-shadow: 0 10px 25px rgba(0,0,0,0.1); display: flex; flex-direction: column; overflow: hidden; }
            .header { background: #2e7d32; color: white; padding: 20px; text-align: center; font-size: 1.2rem; font-weight: bold; }
            .chat-box { flex: 1; padding: 20px; overflow-y: auto; background: #f9f9f9; display: flex; flex-direction: column; gap: 15px; }
            .msg { padding: 12px 16px; border-radius: 15px; max-width: 80%; font-size: 14px; line-height: 1.5; }
            .agent { background: #e8f5e9; color: #2e7d32; align-self: flex-start; border-bottom-left-radius: 2px; }
            .user { background: #1976d2; color: white; align-self: flex-end; border-bottom-right-radius: 2px; }
            .input-area { display: flex; padding: 15px; background: white; border-top: 1px solid #eee; }
            input { flex: 1; padding: 12px; border: 1px solid #ddd; border-radius: 25px; outline: none; padding-left: 20px; }
            button { background: #2e7d32; color: white; border: none; padding: 0 20px; margin-left: 10px; border-radius: 25px; cursor: pointer; }
        </style>
    </head>
    <body>
        <div class="chat-container">
            <div class="header">🌱 智慧大棚 AI 中控</div>
            <div class="chat-box" id="chatBox">
                <div class="msg agent">您好！我是您的 5G 智慧助理。請問有什麼我可以幫您的？</div>
            </div>
            <div class="input-area">
                <input type="text" id="userInput" placeholder="問問大棚溫度..." onkeypress="if(event.key === 'Enter') sendMessage()">
                <button onclick="sendMessage()">發送</button>
            </div>
        </div>
        <script>
            async function sendMessage() {
                const input = document.getElementById('userInput');
                const chatBox = document.getElementById('chatBox');
                const text = input.value.trim();
                if (!text) return;

                chatBox.innerHTML += `<div class="msg user">${text}</div>`;
                input.value = '';
                chatBox.scrollTop = chatBox.scrollHeight;

                const loadingId = "id-" + Date.now();
                chatBox.innerHTML += `<div class="msg agent" id="${loadingId}">思考中... ⚙️</div>`;
                chatBox.scrollTop = chatBox.scrollHeight;

                const formData = new FormData();
                formData.append("message", text);

                try {
                    const response = await fetch('/chat', { method: 'POST', body: formData });
                    const data = await response.json();
                    console.log("後端返回數據:", data); 
                    // 核心修正：確保讀取的是 data.answer
                    document.getElementById(loadingId).innerText = data.answer || "AI 沒有返回內容";
                } catch (e) {
                    document.getElementById(loadingId).innerText = "❌ 出錯了，請檢查後端連線。";
                }
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

# 【後端邏輯】
@app.post("/chat")
def chat_endpoint(message: str = Form(...)):
    print(f"\n🙋‍♂️ 收到前端請求: {message}")
    
    messages = [
        SystemMessage(content="你是一個專業的農業助理。獲取數據後，請簡潔地總結並回答。"),
        HumanMessage(content=message)
    ]
    
    # 1. AI 思考是否用工具
    ai_response = llm_with_tools.invoke(messages)
    messages.append(ai_response)
    
    # 2. 如果 AI 決定用工具
    if ai_response.tool_calls:
        tool_call = ai_response.tool_calls[0]
        args = tool_call["args"]
        print(f"    💡 AI 調用了工具: {tool_call['name']}")
        
        # 執行本地函數
        obs_result = get_sensor_data(
            location=args.get("location", "一號大棚"), 
            sensor_type=args.get("sensor_type", "leaf_temperature")
        )
        
        # 回傳給 AI
        messages.append(ToolMessage(content=obs_result, tool_call_id=tool_call["id"]))
        
        # 3. AI 總結
        print("🤖 AI 正在生成總結...")
        final_response = llm_with_tools.invoke(messages)
        ans = final_response.content.strip()
        
        # 核心修復邏輯：如果 AI 沒說話，後端強制構造句子
        if not ans:
            print("    ⚠️ AI 返回空字符串，執行強制拼接。")
            ans = f"查詢成功：{args.get('location', '指定位置')}的數據目前為 {obs_result}。"
        
        print(f"🎉 最終成果輸出: {ans}")
        return {"answer": ans}

    # 如果沒用工具，直接回 AI 的話
    return {"answer": ai_response.content or "我收到了消息，但暫時無法獲取數據。"}