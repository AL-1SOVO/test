# 檔案名稱：llm_helper.py
import os
import json
from dotenv import load_dotenv
from zhipuai import ZhipuAI

class ZhipuHelper:
    """
    這是一個封裝好的智譜 AI 助手類別 (Class)。
    它把所有繁瑣的底層設定都藏起來，只提供最簡單的介面給外面使用。
    """
    
    def __init__(self, model="glm-4-flash"):
        # 1. 初始化：只要建立這個物件，就自動載入金鑰
        load_dotenv()
        self.api_key = os.getenv("ZHIPUAI_API_KEY")
        if not self.api_key:
            raise ValueError("⚠️ 找不到 API Key，請檢查 .env 檔案！")
        
        self.client = ZhipuAI(api_key=self.api_key)
        self.model = model

    def generate_text(self, system_prompt, user_input, temperature=0.7):
        """專門用來輸出純文字 (例如：聊天、翻譯、總結)"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ],
                temperature=temperature
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"❌ AI 呼叫失敗：{e}")
            return None

    def generate_json(self, system_prompt, user_input, temperature=0.1):
        """專門用來輸出結構化數據 (內建防呆與清道夫邏輯)"""
        # 直接呼叫自己的 generate_text 方法拿原始文字
        raw_result = self.generate_text(system_prompt, user_input, temperature)
        
        if not raw_result:
            return None

        # 清道夫邏輯：剝除 Markdown 外衣
        cleaned_result = raw_result.strip()
        if cleaned_result.startswith('```json'):
            cleaned_result = cleaned_result[7:]
        if cleaned_result.endswith('```'):
            cleaned_result = cleaned_result[:-3]
        cleaned_result = cleaned_result.strip()

        # 轉換為字典
        try:
            return json.loads(cleaned_result)
        except json.JSONDecodeError as e:
            print(f"❌ JSON 解析失敗，AI 沒守規矩！\n原始內容：{raw_result}")
            return None