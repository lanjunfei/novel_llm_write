from django.conf import settings
from openai import OpenAI

# 设置 OpenAI API 密钥
def generate_chapter_content_with_openai(prompt, model="gpt-4"):  # 修改为 gpt-4
    """
    使用 OpenAI ChatCompletion 接口生成章节内容
    :param prompt: 生成内容的提示词
    :param model: 选择使用的模型，默认为 gpt-4
    :return: 生成的章节内容
    """
    try:
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        completion = client.chat.completions.create(  # 使用正确的 ChatCompletion.create 方法
            model=model,
            messages=[  # 使用 messages 传递对话内容
                {"role": "system", "content": "你是一个小说创作助手，帮助生成符合小说整体风格的不少于8000字章节内容。"},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000,
            temperature=1
        )
        # 正确访问生成的内容
        generated_content = completion.choices[0].message.content.strip()
        return generated_content
    except Exception as e:
        print("Error generating content:", str(e))
        return f"(调用 OpenAI 接口出错: {str(e)})"


def extend_chapter_content_with_openai(original_content, multiplier=2):
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
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        completion = client.chat.completions.create(  # 使用正确的 ChatCompletion.create 方法
            model="gpt-4",  # 模型名称
            messages=[  # 使用 messages 传递对话内容
                {"role": "system", "content": "你是一个小说创作高手。"},
                {"role": "user", "content": prompt}
            ],
            max_completion_tokens=6000,
            temperature=1
        )
        # 正确访问扩展后的内容
        expanded_content = completion.choices[0].message.content.strip()
        return expanded_content
    except Exception as e:
        print("Error extending content:", str(e))
        return f"(调用 OpenAI 接口扩展失败: {str(e)})"
