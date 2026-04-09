import os
import json
from dotenv import load_dotenv
from zhipuai import ZhipuAI

# ==========================================
# 1. 系統初始化 (Day 10: 環境變數)
# ==========================================
load_dotenv()
api_key = os.getenv("ZHIPUAI_API_KEY")
if not api_key:
    raise ValueError("⚠️ 找不到 API Key，請檢查 .env 檔案！")

client = ZhipuAI(api_key=api_key)
FILE_NAME = "my_day11tasks.json"

# ==========================================
# 2. 記憶讀寫系統 (文件存取)
# ==========================================
def load_tasks():
    """啟動時，讀取昨天存下來的任務"""
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, 'r', encoding='utf-8') as f:
                return json.load(f)
        except json.JSONDecodeError:
            return [] # 如果檔案壞了，回傳空清單
    return []

def save_tasks(tasks):
    """將任務永久存入硬碟"""
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        # indent=4 讓 JSON 檔案自動換行排版，方便人類閱讀
        json.dump(tasks, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. AI 大腦：處理與排序邏輯 (Day 11: Structured Output)
# ==========================================
def ai_organize_tasks(user_input):
    system_prompt = """
    你是一個專業、高效率的個人任務管家。
    用戶會用一段雜亂的口語告訴你他今天想做的事情。
    請你幫他拆解成具體的任務，評估優先級，並嚴格按照以下 JSON 陣列格式輸出。
    
    【規則】
    1. 不要輸出任何 Markdown 標記 (如 ```json)。
    2. 不要說廢話，只輸出 JSON。
    3. priority (優先級) 只能是："高"、"中"、"低"。

    【輸出格式】
    [
        {"task": "任務名稱", "priority": "高/中/低", "reason": "為什麼給這個優先級(一句話)"},
        {"task": "任務名稱2", "priority": "高/中/低", "reason": "為什麼給這個優先級(一句話)"}
    ]
    """
    try:
        print("⏳ 正在請 AI 管家為您梳理大腦...")
        response = client.chat.completions.create(
            model="glm-4-flashx",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_input}
            ],
            temperature=0.1
        )
        
        raw_result = response.choices[0].message.content.strip()
        
        # 清道夫邏輯
        if raw_result.startswith('```json'):
            raw_result = raw_result[7:]
        if raw_result.endswith('```'):
            raw_result = raw_result[:-3]
        raw_result = raw_result.strip()
        
        return json.loads(raw_result)
        
    except Exception as e:
        print(f"❌ AI 處理失敗：{e}")
        return None

# ==========================================
# 4. 命令行互動介面 (CLI)
# ==========================================
def main():
    print("\n🌟 歡迎使用 AI 任務管家 (CLI 版) 🌟")
    
    # 程式一啟動，先載入硬碟裡的記憶
    tasks = load_tasks()
    
    while True:
        # 顯示當前任務面板
        print("\n" + "="*40)
        print(f"📋 目前待辦清單 ({len(tasks)} 項任務)")
        if not tasks:
            print("  (空空如也，真是清閒的一天！)")
        else:
            for i, t in enumerate(tasks, 1):
                # 簡單的視覺化：根據優先級給不同符號
                icon = "🔴" if t['priority'] == "高" else "🟡" if t['priority'] == "中" else "🟢"
                print(f"[{i}] {icon} {t['task']} - {t['reason']}")
        print("="*40)
        
        # 使用者選單
        print("【選項】1. 碎碎念新增任務  2. 清空所有任務  3. 退出程式")
        choice = input("請選擇 (1/2/3): ")
        
        if choice == '1':
            user_input = input("🗣️ 請隨意輸入你腦袋裡想做的事：\n> ")
            new_tasks = ai_organize_tasks(user_input)
            
            if new_tasks:
                # 將 AI 整理好的新任務，合併到舊的清單中
                tasks.extend(new_tasks)
                save_tasks(tasks)
                print("✅ 任務已為您整理並安全存檔！")
                
        elif choice == '2':
            confirm = input("⚠️ 確定要刪除所有任務嗎？(y/n): ")
            if confirm.lower() == 'y':
                tasks = []
                save_tasks(tasks)
                print("🗑️ 任務已全部清空！")
                
        elif choice == '3':
            print("👋 管家退下，祝您今天效率滿滿！")
            break
            
        else:
            print("⚠️ 錯誤的選擇，請輸入 1, 2 或 3。")

if __name__ == "__main__":
    main()