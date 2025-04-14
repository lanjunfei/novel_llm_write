# novel/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Novel, Chapter, NovelType, NarrativeStyle, NarrativePerspective, Era, NovelReview

class RegisterForm(UserCreationForm):
    email = forms.EmailField(label='邮箱', required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data['email']
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("该邮箱已被注册，请使用其他邮箱或直接登录。")
        return email


class LoginForm(forms.Form):
    username = forms.CharField(label='用户名/邮箱', required=True)
    password = forms.CharField(label='密码', widget=forms.PasswordInput, required=True)
    # 验证码仅允许数字
    captcha = forms.CharField(label='验证码', required=True, max_length=4)


# ---------------------
#   小说相关表单
# ---------------------
class NovelCreateForm(forms.ModelForm):
    """
    新建小说时使用
    """
    class Meta:
        model = Novel
        fields = [
            'title',
            'genre',
            'style',
            'viewpoint',
            'era',
            'location',
            'social_structure',
            'cultural_traits'
        ]
        widgets = {
            'location': forms.Textarea(attrs={'rows': 3}),
            'social_structure': forms.Textarea(attrs={'rows': 3}),
            'cultural_traits': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # 设置外键字段必填 + 查询集
        self.fields['genre'].required = True
        self.fields['style'].required = True
        self.fields['viewpoint'].required = True
        self.fields['era'].required = True

        self.fields['genre'].queryset = NovelType.objects.all()
        self.fields['style'].queryset = NarrativeStyle.objects.all()
        self.fields['viewpoint'].queryset = NarrativePerspective.objects.all()
        self.fields['era'].queryset = Era.objects.all()


class NovelStyleForm(forms.ModelForm):
    """
    编辑“地点设定、社会结构、文化特征”等整体风格时使用
    """
    class Meta:
        model = Novel
        fields = [
            'location',
            'social_structure',
            'cultural_traits'
        ]
        widgets = {
            'location': forms.Textarea(attrs={'rows': 3}),
            'social_structure': forms.Textarea(attrs={'rows': 3}),
            'cultural_traits': forms.Textarea(attrs={'rows': 3}),
        }


# ---------------------
#   章节相关表单
# ---------------------
class ChapterCreateForm(forms.ModelForm):
    """
    新增章节时的表单
    """
    class Meta:
        model = Chapter
        fields = [
            'title',
            'summary',
            'characters_change',
            'conflict',
            'mood',
            'keywords'
        ]
        widgets = {
            'summary': forms.Textarea(attrs={'rows': 3}),
            'characters_change': forms.Textarea(attrs={'rows': 3}),
            'conflict': forms.Textarea(attrs={'rows': 3}),
        }

class ChapterContentForm(forms.ModelForm):
    """章节内容编辑表单"""
    class Meta:
        model = Chapter
        fields = ['title', 'summary', 'order', 'content']  # 添加 order 字段

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['order'].required = False  # `order` 字段不强制输入
        self.fields['content'].widget = forms.Textarea(attrs={'rows': 20, 'cols': 120})

# ---------------------
#   评论/评分表单
# ---------------------
class NovelReviewForm(forms.ModelForm):
    rating = forms.IntegerField(label="打分(1-5)", min_value=1, max_value=5, required=True)

    class Meta:
        model = NovelReview
        fields = ['content', 'rating']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': '写下您的评论...'}),
        }

class ChapterExtendForm(forms.Form):
    MULTIPLIER_CHOICES = [
        (2, '2倍'),
        (3, '3倍'),
    ]
    multiplier = forms.ChoiceField(choices=MULTIPLIER_CHOICES, label="选择扩展倍数", widget=forms.RadioSelect)