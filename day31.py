import os
import json
import random
import time
from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.messages import HumanMessage, ToolMessage
# 大約在第 7 行，把 SystemMessage 加進去
from langchain_core.messages import HumanMessage, ToolMessage, SystemMessage
# 0. 基础设置
load_dotenv()
api_key = os.getenv("ZHIPUAI_API_KEY")
llm = ChatZhipuAI(model="glm-4-flash", api_key=api_key, temperature=0.1)

# ==========================================
# 🛠️ 1. 你的本地真实工具 (Day 30 的升级版)
# ==========================================
def get_sensor_data(location: str, sensor_type: str) -> str:
    print(f"\n   ⚙️ [本地代码执行中] 正在连接 {location} 的 {sensor_type} 传感器...")
    
    if sensor_type == "leaf_temperature":
        result = f"{round(random.uniform(20.0, 35.0), 1)}°C"
    else:
        result = "未知数据"
        
    print(f"   ✅ [本地代码执行完毕] 成功获取数据：{result}\n")
    return result

# ==========================================
# 📄 2. 你的工具说明书 (Day 29 浓缩版)
# ==========================================
get_sensor_data_schema = {
    "type": "function",
    "function": {
        "name": "get_sensor_data",
        "description": "获取一号大棚的农业物联网传感器数据。",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {"type": "string", "description": "位置，例如：大棚、一号车间"},
                "sensor_type": {"type": "string", "enum": ["leaf_temperature", "soil_moisture"], "description": "传感器类型"}
            },
            "required": ["location", "sensor_type"]
        }
    }
}

# 把说明书交给大模型
llm_with_tools = llm.bind_tools([get_sensor_data_schema])

# ==========================================
# 🚀 3. 核心大戏：Agent 对话闭环
# ==========================================
print("🙋‍♂️ 你的问题：大棚里现在的叶片温度是多少？\n")
# 准备对话记录的「公文包」
# 準備對話記錄的「公文包」
messages = [
    # 🌟 加上這段系統指令，給大模型洗腦！
    SystemMessage(content="你是一個專業的農業物聯網中控大腦。你已經內建了所有傳感器的存取權限。當用戶詢問數據時，請『直接調用工具』獲取數據。"),
    
    # 這是你的問題
    HumanMessage(content="一號大棚里现在的土壤湿度是多少？")
]

# 【第一步】大模型思考阶段
print("🤖 AI 思考中 (看说明书决定是否使用工具)...")
ai_response = llm_with_tools.invoke(messages)
messages.append(ai_response) # 把 AI 的回答放回公文包里

# 检查 AI 是否触发了工具调用 (tool_calls)
if ai_response.tool_calls:
    tool_call = ai_response.tool_calls[0]
    tool_name = tool_call["name"]
    tool_args = tool_call["args"]
    
    print(f"   💡 AI 决定暂停聊天，请求调用工具：【{tool_name}】")
    print(f"   💡 AI 提取出的参数：{tool_args}")
    
    # 【第二步】本地代码介入执行
    if tool_name == "get_sensor_data":
        # 把 AI 给的参数解包，传给我们的 Python 函数
        sensor_result = get_sensor_data(
            location=tool_args.get("location"),
            sensor_type=tool_args.get("sensor_type")
        )
        
        # 【第三步】把运行结果汇报给大模型
        # 我们必须用专用的 ToolMessage 包装结果，AI 才知道这是工具跑出来的
        tool_msg = ToolMessage(
            content=sensor_result, 
            tool_call_id=tool_call["id"] # 告诉 AI 对应的工单号
        )
        messages.append(tool_msg) # 把结果放进公文包
        
        # 【第四步】大模型根据数据进行最终总结
        print("🤖 AI 拿到传感器数据，正在生成最终回答...")
        final_response = llm_with_tools.invoke(messages)
        
        print("\n🎉 最终成果输出：")
        print("=" * 40)
        print(final_response.content)
        print("=" * 40)

else:
    print("\nAI 认为不需要工具，直接回答了：")
    print(ai_response.content)