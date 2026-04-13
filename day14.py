# 檔案名稱：day14_app.py

# 直接從你剛剛寫的模組中，把工具箱匯入進來！
from llm_helper import ZhipuHelper

def main():
    # 1. 實例化工具箱 (這行程式碼一跑，金鑰檢查、連線設定就全自動搞定了！)
    ai = ZhipuHelper()

    print("="*40)
    print("測試一：純文字輸出 (翻譯)")
    print("="*40)
    trans_prompt = "你是一個翻譯官，請將使用者的文字翻譯成日文。"
    user_text = "我今天學習了Python的物件導向編程，感覺非常棒！"
    
    # 呼叫變得超級簡單！只要一行！
    jp_text = ai.generate_text(trans_prompt, user_text)
    print(f"原文：{user_text}")
    print(f"翻譯：{jp_text}\n")


    print("="*40)
    print("測試二：JSON 結構化輸出 (新聞提取)")
    print("="*40)
    json_prompt = """
    請提取新聞資訊，並嚴格輸出 JSON，不要 Markdown。
    格式：{"title": "標題", "sentiment": "正面/負面/中立"}
    """
    news = "這家科技公司的最新財報表現亮眼，營收超乎預期，股價大漲。"
    
    # 呼叫 JSON 方法，清道夫邏輯已經在底層默默幫你做完了！
    news_data = ai.generate_json(json_prompt, news)
    print("獲得的字典資料：", news_data)
    print("標題：", news_data['title'])
    print("情感：", news_data['sentiment'])

if __name__ == "__main__":
    main()