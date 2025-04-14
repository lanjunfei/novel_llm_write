# novel/views_read.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Avg, Max
from django.contrib import messages
from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Novel, Chapter, NovelReview
from .forms import NovelReviewForm

class NovelReadListView(ListView):
    """ 已发布小说列表（显示所有公开发布的小说） """
    model = Novel
    template_name = 'read/novel_read_list.html'
    context_object_name = 'novels'
    paginate_by = 10

    def get_queryset(self):
        return Novel.objects.filter(published=True).annotate(
            chapter_count=Count('chapters')
        ).filter(chapter_count__gt=0)  # 使用 '__gt' 来进行大于0的比较
@login_required
def chapter_read_list_view(request, novel_id):
    """
    某本已发布小说的章节列表 -> read/chapter_read_list.html
    """
    novel = get_object_or_404(Novel, id=novel_id, published=True)
    chapters = novel.chapters.filter(published=True).order_by('order')
    return render(request, "read/chapter_read_list.html", {
        "novel": novel,
        "chapters": chapters
    })

@login_required
def chapter_read_view(request, chapter_id):
    """
    单章阅读 -> read/chapter_read.html
    """
    chapter = get_object_or_404(Chapter, id=chapter_id, published=True)
    return render(request, "read/chapter_read.html", {
        "chapter": chapter,
        "novel": chapter.novel
    })

@login_required
def novel_comment_view(request, novel_id):
    """
    小说评论区 -> read/novel_comment.html
    显示读者留言、打分(仅能打一次)
    """
    novel = get_object_or_404(Novel, id=novel_id, published=True)
    reviews = novel.reviews.select_related('user').all()
    has_reviewed = reviews.filter(user=request.user).exists()

    if request.method == 'POST':
        # 若已评论过，不再允许重复评论/打分
        if has_reviewed:
            messages.warning(request, "您已经评论过本小说，不能重复提交。")
            return redirect('novel_comment', novel_id=novel.id)

        form = NovelReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.novel = novel
            review.user = request.user
            review.save()
            messages.success(request, "评论已提交！")
            return redirect('novel_comment', novel_id=novel.id)
    else:
        form = NovelReviewForm()

    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    return render(request, "read/novel_comment.html", {
        "novel": novel,
        "reviews": reviews,
        "form": form,
        "has_reviewed": has_reviewed,
        "avg_rating": avg_rating if avg_rating else 0
    })
