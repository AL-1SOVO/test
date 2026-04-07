import json
import os
from dotenv import load_dotenv
from zhipuai import ZhipuAI

load_dotenv()
api_key = os.getenv("ZHIPUAI_API_KEY")
if not api_key:
    raise ValueError("⚠️ 找不到 API Key！請檢查 .env 檔案是否設定正確。")

client = ZhipuAI(api_key=api_key) 

# 修改点 1：函数现在需要接收“历史记录”作为参数
def get_ai_response(history):
    try:
        response = client.chat.completions.create(
            model="glm-4-flashx", # 使用免费模型
            messages=history      # 修改点 2：直接把整个历史记录列表丢给 AI
        )
        return response.choices[0].message.content
        
    except Exception as e:
        print(f"Error occurred: {e}")
        return "Sorry, I encountered an error."

def start_chat():
    filename = "chat_history.json"
    print("🤖 聊天开始！(输入 'exit' 退出)")
    
    # 修改点 3：在聊天开始前，准备一个空的历史记录本
    # 按照官方格式，有时候可以先放入一句 System prompt 设定 AI 的人设
    conversation_history = [
        {"role": "system", "content": "你是一个非常有帮助的AI助手。"}
    ]

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == 'exit':
            print("Chat ended.")
            break

        # 修改点 4：把用户最新说的话，加到历史记录本里
        conversation_history.append({"role": "user", "content": user_input})

        # 修改点 5：把整本历史记录本递给 AI
        ai_response = get_ai_response(conversation_history)
        print(f"AI: {ai_response}")

        # 修改点 6：把 AI 的回复也加到历史记录本里，为了下一次对话做准备
        conversation_history.append({"role": "assistant", "content": ai_response})

        # 这里的 JSON 存储保持不变，依然用来做长期的本地备份
        chat_history_log = {
            "user": user_input,
            "ai": ai_response
        }
        with open(filename, 'a', encoding='utf-8') as file:
            json.dump(chat_history_log, file, ensure_ascii=False)
            file.write('\n')

if __name__ == "__main__":
    start_chat()