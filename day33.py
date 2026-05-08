import os
import random
import asyncio  # 引入异步 I/O 库
from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage

# ==========================================
# 0. 基础配置
# ==========================================
load_dotenv()
api_key = os.getenv("ZHIPUAI_API_KEY")
llm = ChatZhipuAI(model="glm-4-flash", api_key=api_key, temperature=0.1)

# ==========================================
# 🛠️ 1. 定义异步本地工具 (模拟真实 I/O 阻塞)
# ==========================================
# 【修改 1】将普通函数改为 async def
async def get_sensor_data(location: str, sensor_type: str) -> str:
    print(f"\n   ⚙️ [底层执行] 正在连接 {location} 的 {sensor_type} 传感器...")
    
    # 【修改 2】使用 asyncio.sleep 模拟真实网络请求的延迟 (非阻塞休眠)
    await asyncio.sleep(2)  
    
    if sensor_type == "leaf_temperature":
        result = f"{round(random.uniform(20.0, 35.0), 1)}°C"
    else:
        result = "未知数据"
    print(f"   ✅ [底层执行完毕] 成功获取数据: {result}")
    return result

get_sensor_data_schema = {
    "type": "function",
    "function": {
        "name": "get_sensor_data",
        "description": "获取指定位置的农业物联网传感器数据。",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "位置，例如：大棚、一号车间"},
                "sensor_type": {"type": "string", "enum": ["leaf_temperature"], "description": "传感器类型"}
            },
            "required": ["location", "sensor_type"]
        }
    }
}

llm_with_tools = llm.bind_tools([get_sensor_data_schema])

# ==========================================
# 🚀 2. FastAPI 服务器
# ==========================================
app = FastAPI(title="农业智慧中控 Agent API (异步高并发版)")

@app.get("/", response_class=HTMLResponse)
def chat_ui():
    # 前端 HTML 保持完全不变
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
            <div class="header">🌱 智慧大棚 AI 中控 (Async)</div>
            <div class="chat-box" id="chatBox">
                <div class="msg agent">您好！我是您的 5G 智慧助理。请问有什么我可以帮您的？</div>
            </div>
            <div class="input-area">
                <input type="text" id="userInput" placeholder="问问大棚温度..." onkeypress="if(event.key === 'Enter') sendMessage()">
                <button onclick="sendMessage()">发送</button>
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
                    document.getElementById(loadingId).innerText = data.answer || "AI 没有返回内容";
                } catch (e) {
                    document.getElementById(loadingId).innerText = "❌ 出错了，请检查后端连线。";
                }
                chatBox.scrollTop = chatBox.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

# 【修改 3】路由函数改为 async def
@app.post("/chat")
async def chat_endpoint(message: str = Form(...)):
    print(f"\n🙋‍♂️ 收到前端请求: {message}")
    
    messages = [
        SystemMessage(content="你是一个专业的农业助理。获取数据后，请简洁地总结并回答。"),
        HumanMessage(content=message)
    ]
    
    # 【修改 4】将 invoke 改为 ainvoke，并加上 await 挂起当前任务，让出 CPU
    ai_response = await llm_with_tools.ainvoke(messages)
    messages.append(ai_response)
    
    if ai_response.tool_calls:
        tool_call = ai_response.tool_calls[0]
        args = tool_call["args"]
        print(f"    💡 AI 调用了工具: {tool_call['name']}")
        
        # 【修改 5】执行本地异步函数，必须 await 等待结果
        obs_result = await get_sensor_data(
            location=args.get("location", "一号大棚"), 
            sensor_type=args.get("sensor_type", "leaf_temperature")
        )
        
        messages.append(ToolMessage(content=obs_result, tool_call_id=tool_call["id"]))
        
        print("🤖 AI 正在生成总结...")
        # 【修改 6】再次使用 await ainvoke
        final_response = await llm_with_tools.ainvoke(messages)
        ans = final_response.content.strip()
        
        if not ans:
            print("    ⚠️ AI 返回空字符串，执行强制拼接。")
            ans = f"查询成功：{args.get('location', '指定位置')}的数据目前为 {obs_result}。"
        
        print(f"🎉 最终成果输出: {ans}")
        return {"answer": ans}

    return {"answer": ai_response.content or "我收到了消息，但暂时无法获取数据。"}