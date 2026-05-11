import os
import random
import asyncio
from fastapi import FastAPI, Form, HTTPException
from fastapi.responses import HTMLResponse
from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage

# 基礎配置
load_dotenv()
api_key = os.getenv("ZHIPUAI_API_KEY")
llm = ChatZhipuAI(model="glm-4-flash", api_key=api_key, temperature=0.1)

# ==========================================
# 🛠️ 1. 強化版工具 (帶有異常攔截)
# ==========================================
async def get_sensor_data(location: str, sensor_type: str) -> str:
    print(f"   ⚙️ [底層執行] 嘗試連接 {location}...")
    
    # 🌟 模擬硬體異常：30% 的機率發生連線失敗
    if random.random() < 0.3:
        raise ConnectionError("5G 訊號微弱，感測器節點無響應。")
        
    await asyncio.sleep(1) # 模擬網路延遲
    
    if sensor_type == "leaf_temperature":
        return f"{round(random.uniform(20.0, 35.0), 1)}°C"
    else:
        # 🌟 處理 AI 可能傳入的錯誤參數
        raise ValueError(f"不支援的感測器類型: {sensor_type}")

# 工具說明書保持不變
get_sensor_data_schema = {
    "type": "function",
    "function": {
        "name": "get_sensor_data",
        "description": "獲取指定位置的農業傳感器數據。",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "位置"},
                "sensor_type": {"type": "string", "enum": ["leaf_temperature"], "description": "類型"}
            },
            "required": ["location", "sensor_type"]
        }
    }
}
llm_with_tools = llm.bind_tools([get_sensor_data_schema])

# ==========================================
# 🚀 2. FastAPI 伺服器 (防禦性架構)
# ==========================================
app = FastAPI(title="農業智慧中控 (防禦性編程版)")

@app.get("/", response_class=HTMLResponse)
def chat_ui():
    # HTML 部分維持 Day 32/33 的對話框介面即可
    return ""

@app.post("/chat")
async def chat_endpoint(message: str = Form(...)):
    print(f"\n🙋‍♂️ 收到請求: {message}")
    
    try:
        # 第一階段：AI 思考
        messages = [
            SystemMessage(content="你是一個專業助理。獲取數據後請簡潔回答。"),
            HumanMessage(content=message)
        ]
        
        # 這裡也可能因為 API 金鑰失效或網路問題報錯，所以放在 try 裡面
        ai_response = await llm_with_tools.ainvoke(messages)
        messages.append(ai_response)
        
        if ai_response.tool_calls:
            tool_call = ai_response.tool_calls[0]
            args = tool_call["args"]
            
            # 第二階段：執行工具並攔截特定異常
            try:
                obs_result = await get_sensor_data(
                    location=args.get("location", "一號大棚"), 
                    sensor_type=args.get("sensor_type")
                )
            except ConnectionError as ce:
                # 攔截硬體錯誤，返回 500
                print(f"   ❌ 硬體層錯誤: {ce}")
                raise HTTPException(status_code=500, detail="物聯網設備連線逾時，請檢查大棚 5G 閘道器狀態。")
            except ValueError as ve:
                # 攔截參數錯誤，返回 400
                print(f"   ❌ 參數錯誤: {ve}")
                raise HTTPException(status_code=400, detail=f"非法請求：{str(ve)}")

            # 第三階段：AI 總結
            messages.append(ToolMessage(content=obs_result, tool_call_id=tool_call["id"]))
            final_response = await llm_with_tools.ainvoke(messages)
            return {"answer": final_response.content or f"查詢成功，數值為 {obs_result}"}

        return {"answer": ai_response.content}

    except HTTPException as he:
        # 如果是我們主動拋出的 HTTPException，直接再次拋出讓 FastAPI 處理
        raise he
    except Exception as e:
        # 兜底攔截：捕捉所有未預料到的崩潰，防止噴出 Traceback
        print(f"   🔥 系統級崩潰: {str(e)}")
        raise HTTPException(status_code=500, detail="系統內部異常，中控大腦正在重啟。")