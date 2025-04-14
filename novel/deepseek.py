# novel/deepseek.py
from django.conf import settings
from openai import OpenAI

# 创建独立客户端实例
_deepseek_client = OpenAI(
    api_key=settings.DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"  # 注意参数名改为 base_url
)

def generate_chapter_content_with_deepseek(prompt):
    """
    使用 DeepSeek API 生成章节内容
    :param prompt: 生成内容的提示词
    :return: 生成的章节内容
    """
    try:
        response = _deepseek_client.chat.completions.create(  # 新版调用方式
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个小说创作高手，帮助生成章节内容。"},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        # 使用对象属性访问方式
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise ValueError(f"调用 DeepSeek API 失败: {str(e)}")


def extend_chapter_content_with_deepseek(original_content, multiplier=2):
    """
    扩展章节内容
    :param original_content: 章节的原始内容
    :param multiplier: 扩展倍数，默认为 2 倍
    :return: 扩展后的内容
    """
    prompt = (
        f"请扩展以下内容，使其字数增多{multiplier}倍，只增加原有内容的细节描述，不得加入新的情节。\n"
        f"原内容：\n{original_content}"
    )

    try:
        response = _deepseek_client.chat.completions.create(  # 新版调用方式
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个小说创作高手。"},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise ValueError(f"调用 DeepSeek API 扩展失败: {str(e)}")