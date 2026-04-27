import os
import json
from dotenv import load_dotenv

# 匯入 LangChain 必備組件
from langchain_community.chat_models import ChatZhipuAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field
# ==========================================
# 1. 核心引擎：LangChain 版 MovieRecommender
# ==========================================
class MovieResponse(BaseModel):
    movie_name: str = Field(description="電影的名稱")
    genre: str = Field(description="電影的類型")
    reason: str = Field(description="推薦這部電影的理由")

class MovieRecommender:
    def __init__(self):
        load_dotenv()
        api_key = os.getenv("ZHIPUAI_API_KEY")
        if not api_key:
            raise ValueError("⚠️ 找不到 API Key")

        # A. 模型積木
        self.llm = ChatZhipuAI(
            api_key=api_key, 
            model="glm-4-flash", 
            temperature=0.7
        )

        # B. 解析器積木 (這就是取代你手寫「清道夫」的神器)
        # 🌟 修改這一行：把緊箍咒套到 Parser 頭上
        self.parser = JsonOutputParser(pydantic_object=MovieResponse)
        
        # ... (後面的 prompt 和 chain 都不用動！)

        # C. 提示詞模板積木
        # 我們利用 parser.get_format_instructions() 自動產生 JSON 格式要求
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一個資深的電影推薦專家。請根據用戶的心情推薦一部電影。\n{format_instructions}"),
            ("user", "{mood}")
        ]).partial(format_instructions=self.parser.get_format_instructions())

        # D. 組裝流水線 (Chain)
        self.chain = self.prompt | self.llm | self.parser

    def get_recommendation(self, user_mood):
        try:
            # 直接執行流水線，回傳的就是乾乾淨淨的「字典」
            return self.chain.invoke({"mood": user_mood})
        except Exception as e:
            print(f"❌ LangChain 處理出錯：{e}")
            return None

# ==========================================
# 2. 記憶系統 (保持不變，這是標準 Python 邏輯)
# ==========================================
FILE_NAME = "history.json"

def load_history():
    if os.path.exists(FILE_NAME):
        try:
            with open(FILE_NAME, 'r', encoding='utf-8') as f:
                return json.load(f)
        except: return []
    return []

def save_history(new_movie_dict):
    history_list = load_history()
    history_list.append(new_movie_dict)
    with open(FILE_NAME, 'w', encoding='utf-8') as f:
        json.dump(history_list, f, ensure_ascii=False, indent=4)

# ==========================================
# 3. 主程式
# ==========================================
def main():
    print("🍿 歡迎來到 LangChain 電影院 🍿")
    ai = MovieRecommender()

    while True:
        mood = input("\n👉 心情或想看什麼？(q退出): ")
        if mood.lower() == 'q': break
            
        print("⏳ LangChain 流水線運作中...")
        result = ai.get_recommendation(mood)
        
        if result:
            print("\n✅ 推薦成功！")
            # 注意：這裡直接用字典取值
            print(f"🎬 片名：{result.get('movie_name')}")
            print(f"🎭 類型：{result.get('genre')}")
            print(f"💡 理由：{result.get('reason')}")
            save_history(result)

if __name__ == "__main__":
    main()