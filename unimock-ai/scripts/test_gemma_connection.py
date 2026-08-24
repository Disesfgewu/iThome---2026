import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("未找到 GEMINI_API_KEY，請確認 .env 檔案設定。")

genai.configure(api_key=api_key)

def verify_connection():
    print("🔍 正在連接 Google AI Studio 獲取可用模型列表...")
    models = genai.list_models()
    print("✅ 可用模型列表：")
    for m in models:
        if 'generateContent' in m.supported_generation_methods:
            print(f"  - {m.name}")

    print("\n🚀 正在測試 Gemma-4-31B-it 生成對話...")
    model = genai.GenerativeModel('gemma-4-31b-it')
    response = model.generate_content("請簡短用一句話介紹自己，並說明你如何協助大學升學模擬面試。")
    print(f"🤖 模型回應：\n{response.text}")

if __name__ == "__main__":
    verify_connection()