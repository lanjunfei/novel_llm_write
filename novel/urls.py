# novel/urls.py
from django.urls import path
from .views import (
    NovelListView,
    novel_create_view,
    novel_style_view,
    NovelDeleteView,
    publish_novel,
    unpublish_novel,

    ChapterListView,
    ChapterCreateView,
    ChapterDeleteView,
    publish_chapter,
    unpublish_chapter,
    chapter_content_view,
    chapter_style_view,
    chapter_extend_view,
)
from .views_auth import (
    register_view,
    login_view,
    logout_view,
    activate_account,
    captcha_image,
)
from .views_read import (
    NovelReadListView,
    chapter_read_list_view,
    chapter_read_view,
    novel_comment_view,
)
from django.contrib.auth import views as auth_views

urlpatterns = [
    # 用户认证
    path('accounts/register/', register_view, name='register'),
    path('accounts/login/', login_view, name='login'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/activate/<uidb64>/<token>/', activate_account, name='activate_account'),
    path('accounts/captcha/', captcha_image, name='captcha_image'),

    # 密码重置相关
    path('accounts/password_reset/',
         auth_views.PasswordResetView.as_view(
             template_name='registration/password_reset_form.html',
             email_template_name='registration/password_reset_email.html',
             success_url='/accounts/password_reset/done/'
         ),
         name='password_reset'),
    path('accounts/password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
             template_name='registration/password_reset_done.html'
         ),
         name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
             template_name='registration/password_reset_confirm.html',
             success_url='/accounts/reset/done/'
         ),
         name='password_reset_confirm'),
    path('accounts/reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
             template_name='registration/password_reset_complete.html'
         ),
         name='password_reset_complete'),

    # ========== “我的小说”管理区 ==========
    path('', NovelListView.as_view(), name='novel_list'),                      # 主页: 我的小说列表
    path('novel/new/', novel_create_view, name='novel_create'),                # 新建小说
    path('novel/<int:pk>/style/', novel_style_view, name='novel_style'),       # 编辑小说整体风格
    path('novel/<int:pk>/delete/', NovelDeleteView.as_view(), name='novel_delete'),
    path('novel/<int:pk>/publish/', publish_novel, name='novel_publish'),
    path('novel/<int:pk>/unpublish/', unpublish_novel, name='novel_unpublish'),

    # 章节管理
    path('novel/<int:novel_id>/chapters/', ChapterListView.as_view(), name='chapter_list'),
    path('novel/<int:novel_id>/chapter/new/', ChapterCreateView.as_view(), name='chapter_create'),
    path('chapter/<int:chapter_id>/delete/', ChapterDeleteView.as_view(), name='chapter_delete'),
    path('chapter/<int:chapter_id>/publish/', publish_chapter, name='chapter_publish'),
    path('chapter/<int:chapter_id>/unpublish/', unpublish_chapter, name='chapter_unpublish'),
    path('chapter/<int:chapter_id>/content/', chapter_content_view, name='chapter_content'),
    path('chapter/<int:chapter_id>/style/', chapter_style_view, name='chapter_style'),
    path('chapter/<int:chapter_id>/extend/', chapter_extend_view, name='chapter_extend'),
    # ========== “阅读区” ==========
    path('read/novels/', NovelReadListView.as_view(), name='novel_read_list'),            # 已发布小说列表
    path('read/novel/<int:novel_id>/chapters/', chapter_read_list_view, name='chapter_read_list'),
    path('read/chapter/<int:chapter_id>/', chapter_read_view, name='chapter_read'),
    path('read/novel/<int:novel_id>/comment/', novel_comment_view, name='novel_comment'),
]

