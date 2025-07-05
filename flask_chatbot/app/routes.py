from flask import render_template, request, jsonify
from app import app
from app.data_provider import DataProvider
from app.deepseek_api import DeepSeekClient

# 初始化数据提供器和API客户端
data_provider = DataProvider()
deepseek_client = DeepSeekClient()


@app.route("/")
def index():
    """渲染聊天界面"""
    return render_template("index.html")


@app.route("/api/chat", methods=["POST"])
def chat():
    """处理聊天请求的API接口"""
    data = request.get_json()
    user_question = data.get("question", "").strip()

    if not user_question:
        return jsonify({"status": "error", "answer": "请输入问题内容"})

    try:
        # 1. 获取分析数据上下文
        context = data_provider.get_analysis_context()

        # 2. 调用DeepSeek API获取回答
        answer = deepseek_client.chat_completion(user_question, context)

        return jsonify({"status": "success", "answer": answer})
    except Exception as e:
        app.logger.error(f"聊天处理失败: {str(e)}")
        return jsonify({"status": "error", "answer": f"处理失败：{str(e)}"})