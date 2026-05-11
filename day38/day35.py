import os
import random
import asyncio
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import StreamingResponse  # 🌟 關鍵：流式響應
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage

# 基礎配置
load_dotenv()
api_key = os.getenv("ZHIPUAI_API_KEY")
llm = ChatZhipuAI(model="glm-4-flash", api_key=api_key, temperature=0.1)

app = FastAPI(title="農業智慧中控：Day 39 流式版")

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 模擬傳感器工具
async def get_sensor_data(location: str, sensor_type: str) -> str:
    await asyncio.sleep(1.5)  # 模擬 5G 延遲
    if sensor_type == "leaf_temperature":
        return f"{round(random.uniform(20.0, 32.0), 1)}°C"
    return "數據暫缺"

tools = [{
    "type": "function",
    "function": {
        "name": "get_sensor_data",
        "description": "獲取智慧農業傳感器數據",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "位置"},
                "sensor_type": {"type": "string", "enum": ["leaf_temperature"], "description": "類型"}
            },
            "required": ["location", "sensor_type"]
        }
    }
}]
llm_with_tools = llm.bind_tools(tools)

# 🏢 窗口 1：傳統 POST 路由 (保持向下相容)
@app.post("/chat")
async def chat_endpoint(message: str = Form(...)):
    messages = [HumanMessage(content=message)]
    response = await llm_with_tools.ainvoke(messages)
    return {"answer": response.content}

# 🏢 窗口 2：流式 POST 路由 (Day 39 新增)
@app.post("/chat_stream")
async def chat_stream_endpoint(message: str = Form(...)):
    
    async def event_generator():
        messages = [
            SystemMessage(content="你是一個專業農業助理。獲取數據後，請給出簡短友善的總結。"),
            HumanMessage(content=message)
        ]
        
        # 第一階段：判斷是否需要調用工具 (不流式)
        ai_msg = await llm_with_tools.ainvoke(messages)
        messages.append(ai_msg)
        
        if ai_msg.tool_calls:
            yield "📡 正在調取 5G 傳感器數據...\n\n"
            tool_call = ai_msg.tool_calls[0]
            obs = await get_sensor_data(tool_call["args"].get("location"), tool_call["args"].get("sensor_type"))
            messages.append(ToolMessage(content=obs, tool_call_id=tool_call["id"]))
            
            # 第二階段：對最終結果進行流式輸出 (astream)
            async for chunk in llm_with_tools.astream(messages):
                if chunk.content:
                    yield chunk.content
        else:
            # 如果只是普通對話，直接流式輸出內容
            for char in ai_msg.content:
                yield char
                await asyncio.sleep(0.01)

    return StreamingResponse(event_generator(), media_type="text/event-stream")