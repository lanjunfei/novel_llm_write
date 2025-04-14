from django.contrib import admin
from .models import Novel, Chapter, NovelType, NarrativeStyle, NarrativePerspective, Era, NovelReview
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.db.models import Max, Count, Avg

# 自定义用户管理，显示激活状态，允许手动激活
class UserAdmin(DefaultUserAdmin):
    list_display = ('id', 'username', 'email', 'is_active', 'is_staff', 'date_joined')
    list_filter = ('is_active', 'is_staff', 'date_joined')
    search_fields = ('username', 'email')
    list_editable = ('is_active', 'is_staff')  # 添加字段可编辑

    actions = ['activate_users']

    def activate_users(self, request, queryset):
        """管理员批量激活用户"""
        count = queryset.update(is_active=True)
        self.message_user(request, f"成功激活 {count} 个用户")
    activate_users.short_description = "激活选中的用户"

# 取消默认的 User 注册，改用自定义的 UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

@admin.register(Novel)
class NovelAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'user',
        'get_genre',
        'published_status',
        'created_at',
        'get_average_rating',  # 显示评论的平均评分
        'get_review_count'     # 显示评论数量
    )
    list_select_related = ['genre', 'user']
    list_filter = ('genre__name', 'published', 'created_at')
    search_fields = ('title', 'user__username')
    date_hierarchy = 'created_at'
    raw_id_fields = ('user',)
    list_per_page = 20  # 每页显示20个条目

    def get_genre(self, obj):
        return obj.genre.name if obj.genre else '-'
    get_genre.short_description = '类型'

    def published_status(self, obj):
        return '已发布' if obj.published else '草稿'
    published_status.short_description = '状态'

    def get_average_rating(self, obj):
        """计算小说的平均评分"""
        return obj.reviews.aggregate(average_rating=Avg('rating'))['average_rating'] or 0
    get_average_rating.short_description = '平均评分'

    def get_review_count(self, obj):
        """计算评论数量"""
        return obj.reviews.count()
    get_review_count.short_description = '评论数'


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ('novel_title', 'order', 'created_at')  # 只显示必要的字段
    search_fields = ('novel__title', 'title')
    list_filter = ('novel__title',)
    autocomplete_fields = ['novel']
    list_editable = ['order']  # 允许编辑章节顺序

    def novel_title(self, obj):
        return obj.novel.title
    novel_title.short_description = '小说标题'
# 统一注册可配置选项
@admin.register(NovelType)
class NovelTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_custom')
    list_editable = ('is_custom',)

@admin.register(NarrativeStyle)
class NarrativeStyleAdmin(NovelTypeAdmin):
    pass

@admin.register(NarrativePerspective)
class NarrativePerspectiveAdmin(NovelTypeAdmin):
    pass

@admin.register(Era)
class EraAdmin(NovelTypeAdmin):
    pass

# ---------------------------
# 新增评论管理界面
# ---------------------------
@admin.register(NovelReview)
class NovelReviewAdmin(admin.ModelAdmin):
    list_display = ('novel', 'user', 'rating', 'created_at')
    list_filter = ('created_at', 'rating')
    search_fields = ('novel__title', 'user__username')

    def get_user(self, obj):
        return obj.user.username
    get_user.short_description = '用户'

    def get_novel(self, obj):
        return obj.novel.title
    get_novel.short_description = '小说标题'
