# 小说创作助手 (AI Novel Writing Assistant)

基于 Django 和大型语言模型 (LLM) 的小说创作平台，帮助用户利用 AI 写作能力快速创作小说。

## 项目概述

该项目是一个 Web 应用程序，允许用户创建、编辑和发布小说。它利用 OpenAI (GPT-4) 和 DeepSeek 的大型语言模型来生成和扩展小说内容，帮助用户更高效地进行创意写作。

## 主要功能

- **用户管理**：用户注册、登录、密码重置等功能
- **小说管理**：创建、编辑、发布和删除小说
- **章节管理**：为小说创建和管理多个章节
- **AI 辅助创作**：
  - 基于用户输入的提示自动生成章节内容
  - 支持内容扩展功能，增加文本细节
  - 集成多种 LLM 模型 (OpenAI GPT-4, DeepSeek)
- **个性化设置**：
  - 设置小说类型、叙事风格、视角和时代背景
  - 自定义地点设定、社会结构和文化特征
- **发布系统**：控制小说和章节的发布状态
- **评分和评论**：用户可以对已发布的小说进行评分和评论

## 技术栈

- **后端框架**：Django 5.1.6
- **数据库**：MySQL
- **AI 集成**：
  - OpenAI API (使用 GPT-4 模型)
  - DeepSeek API
- **前端**：
  - HTML/CSS/JavaScript
  - Django 模板系统

## 安装与设置

### 前提条件

- Python 3.8+
- MySQL
- OpenAI API 密钥和/或 DeepSeek API 密钥

### 安装步骤

1. 克隆项目仓库

```bash
git clone <repository-url>
cd xiaoshuo
```

2. 创建并激活虚拟环境

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/MacOS
source venv/bin/activate
```

3. 安装依赖包

```bash
pip install -r requirements.txt
```

4. 配置数据库

在 `xiaoshuo/settings.py` 中配置数据库连接信息：

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'novel',
        'USER': 'your_username',
        'PASSWORD': 'your_password',
        'HOST': '127.0.0.1',
        'PORT': '3306',
    }
}
```

5. 配置 API 密钥

在 `xiaoshuo/settings.py` 中配置 API 密钥：

```python
OPENAI_API_KEY = "your_openai_api_key"
DEEPSEEK_API_KEY = "your_deepseek_api_key"
```

6. 创建数据库表

```bash
python manage.py migrate
```

7. 创建超级用户

```bash
python manage.py createsuperuser
```

8. 运行开发服务器

```bash
python manage.py runserver
```

## 使用指南

### 创建小说

1. 登录系统
2. 在主页点击"创建新小说"
3. 填写小说的基本信息（标题、类型、风格等）
4. 保存后可以进一步编辑小说的整体设定

### 创建章节

1. 在小说详情页点击"添加章节"
2. 填写章节的设计信息（标题、关键词、人物变化等）
3. 系统将自动调用 AI 模型生成章节内容
4. 可以进一步编辑生成的内容或使用内容扩展功能

### 发布小说

1. 在小说列表中找到要发布的小说
2. 点击"发布"按钮将小说设为公开状态
3. 发布小说后，还需单独发布各个章节

## 数据模型

- **Novel**：小说模型，包含标题、类型、风格等基本信息
- **Chapter**：章节模型，包含章节标题、内容、摘要等
- **NovelReview**：小说评论与评分模型
- **自定义选项模型**：
  - NovelType：小说类型
  - NarrativeStyle：叙事风格
  - NarrativePerspective：叙事视角
  - Era：时代背景

## 注意事项

- API 密钥应妥善保管，避免泄露
- 生成的小说内容可能需要额外的审核和编辑
- 使用 AI 生成内容时应注意遵守相关法律法规和平台政策