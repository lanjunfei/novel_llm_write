# novel/views.py
from django.db.models.functions import Length
from django.urls import reverse_lazy, reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Max, Count, Sum, F, Q
from django.views.generic import (
    ListView, CreateView, UpdateView, DeleteView, DetailView
)
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Novel, Chapter
from .forms import (
    NovelCreateForm,
    NovelStyleForm,
    ChapterCreateForm,
    ChapterContentForm
)
from .openai import generate_chapter_content_with_openai, extend_chapter_content_with_openai  # 导入 OpenAI 相关函数
from .deepseek import generate_chapter_content_with_deepseek, extend_chapter_content_with_deepseek  # 导入 DeepSeek 相关函数


# ==============================
# 小说管理视图（我的小说）
# ==============================
class NovelListView(LoginRequiredMixin, ListView):
    model = Novel
    template_name = "novel/index.html"
    context_object_name = "novels"

    def get_queryset(self):
        return Novel.objects.filter(user=self.request.user) \
            .annotate(
                chapter_count=Count('chapters'),
                total_words=Sum(Length('chapters__content'))
            ) \
            .order_by('-created_at')
@login_required
def novel_create_view(request):
    """
    新建小说 -> novel_create.html
    """
    if request.method == "POST":
        form = NovelCreateForm(request.POST)
        if form.is_valid():
            novel = form.save(commit=False)
            novel.user = request.user
            novel.save()
            messages.success(request, "小说创建成功！")
            return redirect("novel_list")
    else:
        form = NovelCreateForm()
    return render(request, "novel/novel_create.html", {"form": form})

@login_required
def novel_style_view(request, pk):
    """
    整体设计编辑 -> novel_style.html
    只能编辑：地点设定、社会结构、文化特征
    """
    novel = get_object_or_404(Novel, pk=pk, user=request.user)
    if request.method == "POST":
        form = NovelStyleForm(request.POST, instance=novel)
        if form.is_valid():
            form.save()
            messages.success(request, "小说整体风格已保存！")
            return redirect("novel_list")
    else:
        form = NovelStyleForm(instance=novel)
    return render(request, "novel/novel_style.html", {"form": form, "novel": novel})

class NovelDeleteView(LoginRequiredMixin, DeleteView):
    """
    删除小说 -> novel_delete.html
    """
    model = Novel
    template_name = 'novel/novel_delete.html'

    def get_queryset(self):
        # 只允许删除自己的小说
        return Novel.objects.filter(user=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "小说删除成功！")
        return reverse_lazy('novel_list')


@login_required
def publish_novel(request, pk):
    """
    发布小说
    """
    novel = get_object_or_404(Novel, pk=pk, user=request.user)
    novel.published = True
    novel.save()
    messages.success(request, "小说已发布！")
    return redirect('novel_list')

@login_required
def unpublish_novel(request, pk):
    """
    取消发布小说
    """
    novel = get_object_or_404(Novel, pk=pk, user=request.user)
    novel.published = False
    novel.save()
    # 同时取消所有章节已发布状态(可选)
    novel.chapters.update(published=False)
    messages.success(request, "小说已取消发布！")
    return redirect('novel_list')

# ==============================
# 章节管理视图
# ==============================
class ChapterListView(LoginRequiredMixin, ListView):
    """
    章节列表 -> chapter_list.html
    """
    model = Chapter
    template_name = "novel/chapter_list.html"
    context_object_name = "chapters"

    def get_queryset(self):
        novel = get_object_or_404(Novel, id=self.kwargs["novel_id"], user=self.request.user)
        return Chapter.objects.filter(novel=novel).order_by("order")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['novel'] = get_object_or_404(Novel, id=self.kwargs["novel_id"], user=self.request.user)
        return context

class ChapterDeleteView(LoginRequiredMixin, DeleteView):
    """
    删除章节 -> chapter_delete.html
    """
    model = Chapter
    template_name = 'novel/chapter_delete.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Chapter, id=self.kwargs['chapter_id'], novel__user=self.request.user)

    def get_success_url(self):
        messages.success(self.request, "章节删除成功！")
        return reverse('chapter_list', kwargs={'novel_id': self.object.novel.id})


@login_required
def chapter_content_view(request, chapter_id):
    """
    编辑章节内容 -> chapter_content.html
    只显示正文，可人工修改保存
    """
    chapter = get_object_or_404(Chapter, id=chapter_id, novel__user=request.user)
    if request.method == 'POST':
        form = ChapterContentForm(request.POST, instance=chapter)
        if form.is_valid():
            form.save()
            messages.success(request, "章节内容已保存！")
            return redirect('chapter_list', novel_id=chapter.novel.id)
    else:
        form = ChapterContentForm(instance=chapter)
    return render(request, "novel/chapter_content.html", {"form": form, "chapter": chapter})


@login_required
def chapter_style_view(request, chapter_id):
    """
    查看章节设计 -> chapter_style.html
    只读：标题、摘要、人物变化、冲突、氛围、关键词
    """
    chapter = get_object_or_404(Chapter, id=chapter_id, novel__user=request.user)
    return render(request, "novel/chapter_style.html", {"chapter": chapter})


@login_required
def publish_chapter(request, chapter_id):
    """
    发布章节：只有当小说已发布时才可发布章节
    """
    chapter = get_object_or_404(Chapter, id=chapter_id, novel__user=request.user)
    if not chapter.novel.published:
        messages.warning(request, "请先发布小说，再发布章节！")
    else:
        chapter.published = True
        chapter.save()
        messages.success(request, "章节已发布！")
    return redirect('chapter_list', novel_id=chapter.novel.id)

@login_required
def unpublish_chapter(request, chapter_id):
    """
    取消发布章节
    """
    chapter = get_object_or_404(Chapter, id=chapter_id, novel__user=request.user)
    chapter.published = False
    chapter.save()
    messages.success(request, "章节已取消发布！")
    return redirect('chapter_list', novel_id=chapter.novel.id)


@login_required
def chapter_edit_view(request, chapter_id):
    """ 章节编辑页面，允许作者修改章节顺序 """
    chapter = get_object_or_404(Chapter, id=chapter_id, novel__user=request.user)

    if request.method == 'POST':
        form = ChapterContentForm(request.POST, instance=chapter)
        if form.is_valid():
            # 保存章节顺序
            chapter.order = form.cleaned_data['order']
            form.save()
            messages.success(request, "章节更新成功！")
            return redirect('chapter_list', novel_id=chapter.novel.id)
    else:
        form = ChapterContentForm(instance=chapter)

    return render(request, 'novel/chapter_edit.html', {'form': form, 'chapter': chapter})


# ==============================
# 小说管理视图（我的小说）
# ==============================
class ChapterCreateView(LoginRequiredMixin, CreateView):
    """
    新增章节 -> chapter_create.html
    自动调用大模型生成正文
    """
    model = Chapter
    form_class = ChapterCreateForm
    template_name = 'novel/chapter_create.html'

    def form_valid(self, form):
        novel = get_object_or_404(Novel, pk=self.kwargs['novel_id'], user=self.request.user)
        chapter = form.save(commit=False)
        chapter.novel = novel

        # 自动计算章节顺序
        max_order = novel.chapters.aggregate(max_order=Max('order'))['max_order']
        chapter.order = (max_order + 1) if max_order else 1

        # 获取模型选择
        model_choice = self.request.POST.get("model_choice", "openai")  # 默认为 OpenAI

        # 生成章节内容
        prompt = (
            "请根据以下小说整体背景设定及章节信息生成章节内容：\n\n"
            f"【小说整体背景】\n"
            f"标题：{novel.title}\n"
            f"类型：{novel.genre.name if novel.genre else '未知'}\n"
            f"风格：{novel.style.name if novel.style else '未知'}\n"
            f"视角：{novel.viewpoint.name if novel.viewpoint else '未知'}\n"
            f"时代：{novel.era.name if novel.era else '未知'}\n"
            f"地点：{novel.location}\n"
            f"社会结构：{novel.social_structure}\n"
            f"文化特征：{novel.cultural_traits}\n\n"
            "【章节信息】\n"
            f"标题：{chapter.title}\n"
            f"摘要：{chapter.summary}\n"
            f"角色变化：{chapter.characters_change}\n"
            f"冲突：{chapter.conflict}\n"
            f"氛围：{chapter.mood}\n"
            f"关键字：{chapter.keywords}\n\n"
            "请生成本章的具体正文："
        )

        if model_choice == "openai":
            generated_content = generate_chapter_content_with_openai(prompt)
        else:  # 使用 DeepSeek
            generated_content = generate_chapter_content_with_deepseek(prompt)

        chapter.content = generated_content
        chapter.save()

        messages.success(self.request, "章节创建并生成正文成功！")
        return redirect('chapter_list', novel_id=novel.id)

@login_required
def chapter_extend_view(request, chapter_id):
    """章节内容扩展视图"""
    chapter = get_object_or_404(Chapter, id=chapter_id)

    if request.method == 'POST':
        extension_multiplier = int(request.POST.get('multiplier', 2))  # 获取扩展倍数（默认为2倍）

        # 获取章节原有内容
        original_content = chapter.content

        # 获取模型选择
        model_choice = request.POST.get("model_choice", "openai")  # 默认为 OpenAI

        try:
            # 调用相应的扩展函数
            if model_choice == "openai":
                expanded_content = extend_chapter_content_with_openai(original_content, extension_multiplier)
            else:  # 使用 DeepSeek
                expanded_content = extend_chapter_content_with_deepseek(original_content, extension_multiplier)

            # 替换章节内容
            chapter.content = expanded_content
            chapter.save()

            messages.success(request, "章节内容扩展成功！")
            return redirect('chapter_content', chapter_id=chapter.id)
        except ValueError as e:
            messages.error(request, f"扩展失败：{str(e)}")
            return redirect('chapter_extend', chapter_id=chapter.id)

    return render(request, "novel/chapter_extend.html", {"chapter": chapter})
