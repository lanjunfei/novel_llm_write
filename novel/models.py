# novel/models.py
from django.db import models
from django.contrib.auth.models import User

class CustomizableOption(models.Model):
    """抽象基类用于可自定义选项"""
    name = models.CharField(max_length=50, unique=True)
    is_custom = models.BooleanField(default=False, verbose_name="用户自定义")

    class Meta:
        abstract = True

    def __str__(self):
        return self.name

class NovelType(CustomizableOption):
    class Meta:
        verbose_name = "小说类型"
        verbose_name_plural = "小说类型"

class NarrativeStyle(CustomizableOption):
    class Meta:
        verbose_name = "叙事风格"
        verbose_name_plural = "叙事风格"

class NarrativePerspective(CustomizableOption):
    class Meta:
        verbose_name = "叙事视角"
        verbose_name_plural = "叙事视角"

class Era(CustomizableOption):
    class Meta:
        verbose_name = "时代背景"
        verbose_name_plural = "时代背景"

class Novel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="用户")
    title = models.CharField(max_length=100, verbose_name="标题")
    genre = models.ForeignKey(NovelType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="类型")
    style = models.ForeignKey(NarrativeStyle, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="风格")
    viewpoint = models.ForeignKey(NarrativePerspective, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="视角")
    era = models.ForeignKey(Era, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="时代")
    location = models.TextField(blank=True, null=True, verbose_name="地点设定")
    social_structure = models.TextField(blank=True, null=True, verbose_name="社会结构")
    cultural_traits = models.TextField(blank=True, null=True, verbose_name="文化特征")
    details = models.JSONField(default=dict, verbose_name="详细信息")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    published = models.BooleanField(default=False, verbose_name="已发布")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "小说"
        verbose_name_plural = "小说"

    def __str__(self):
        return self.title

class Chapter(models.Model):
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='chapters', verbose_name="所属小说")
    title = models.CharField(max_length=100, blank=True, default='', verbose_name="章节标题")
    summary = models.TextField(blank=True, default='', verbose_name="章节概要")  # 保留章节概要
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    order = models.PositiveIntegerField(default=0, verbose_name="章节顺序")
    characters_change = models.TextField(blank=True, default='', verbose_name="人物变化")
    conflict = models.TextField(blank=True, default='', verbose_name="矛盾冲突")
    mood = models.CharField(max_length=50, blank=True, default='', verbose_name="氛围基调")
    keywords = models.CharField(max_length=200, blank=True, default='', verbose_name="关键词")
    content = models.TextField(blank=True, verbose_name="章节内容")
    published = models.BooleanField(default=False, verbose_name="已发布")

    class Meta:
        ordering = ['order', 'created_at']  # 默认按照序号排序，若无序号按时间排序
        verbose_name = "章节"
        verbose_name_plural = "章节"

    def save(self, *args, **kwargs):
        if not self.order:
            # 默认将章节的序号按创建时间的时间戳赋值
            self.order = int(self.created_at.timestamp())
        super().save(*args, **kwargs)

class NovelReview(models.Model):
    """
    小说评论与评分模型：
    - 一个用户对同一本小说只能评论一次(含评分)。
    - rating为1~5的整数。
    """
    novel = models.ForeignKey(Novel, on_delete=models.CASCADE, related_name='reviews', verbose_name="所属小说")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="评论用户")
    content = models.TextField(blank=True, default='', verbose_name="评论内容")
    rating = models.PositiveIntegerField(default=5, verbose_name="评分(1-5)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="评论时间")

    class Meta:
        unique_together = ('novel', 'user')
        verbose_name = "小说评论"
        verbose_name_plural = "小说评论"

    def __str__(self):
        return f"评论[{self.novel.title}] by {self.user.username}"

