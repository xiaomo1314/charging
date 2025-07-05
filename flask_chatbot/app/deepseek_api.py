import requests
from app import app


class DeepSeekClient:
    def __init__(self):
        self.api_key = app.config["DEEPSEEK_API_KEY"]
        self.api_url = app.config["DEEPSEEK_API_URL"]
        self.model = app.config["DEEPSEEK_MODEL"]

        if not self.api_key:
            app.logger.warning("未配置DeepSeek API密钥，将无法正常调用")

    def chat_completion(self, user_question, context):
        """
        调用DeepSeek API获取回答
        :param user_question: 用户问题
        :param context: 充电桩分析数据上下文
        :return: 回答文本或错误信息
        """
        if not self.api_key:
            return "请先配置DeepSeek API密钥"



        print(f"请求URL: {self.api_url}")



        # 构造系统提示（结合分析数据）
        system_prompt = f"""
        你是充电桩分析系统的智能助手，以下是2023年3月的关键分析数据：
        {context}

        请基于上述数据回答用户问题，遵循以下规则：
        1. 回答需准确引用数据，数据保留两位小数
        2. 若问题与充电桩分析无关，礼貌拒绝并引导询问相关话题
        3. 若数据中没有相关信息，明确说明"未查询到该数据"
        4. 语言简洁易懂，避免使用专业术语
        """

        # API请求参数
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt.strip()},
                {"role": "user", "content": user_question}
            ],
            "temperature": 0.6,  # 控制回答随机性
            "max_tokens": 500  # 最大回答长度
        }

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        try:
            response = requests.post(
                self.api_url,
                json=payload,
                headers=headers,
                timeout=10  # 10秒超时
            )
            response.raise_for_status()  # 抛出HTTP错误

            # 解析响应
            result = response.json()
            if "choices" in result and len(result["choices"]) > 0:
                return result["choices"][0]["message"]["content"]
            else:
                return "未获取到有效回答，请重试"

        except requests.exceptions.HTTPError as e:
            app.logger.error(f"API请求错误: {str(e)}")
            return f"请求失败（HTTP错误）：{str(e)}"
        except requests.exceptions.Timeout:
            app.logger.error("API请求超时")
            return "请求超时，请稍后重试"
        except Exception as e:
            app.logger.error(f"API调用异常: {str(e)}")
            return f"处理失败：{str(e)}"