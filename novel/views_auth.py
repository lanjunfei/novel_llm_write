# novel/views_auth.py
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str, force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.core.mail import send_mail
from django.http import HttpResponse
from django.conf import settings
from django.urls import reverse
from io import BytesIO
import random
from PIL import Image, ImageDraw, ImageFont
import re

from .forms import RegisterForm, LoginForm

User = get_user_model()

def register_view(request):
    """用户注册"""
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True   # 注册后需激活
            user.save()
            messages.success(request, "注册成功！请前往邮箱激活账号。")
            return redirect("login")
    else:
        form = RegisterForm()
    return render(request, "registration/register.html", {"form": form})


def activate_account(request, uidb64, token):
    """激活账号"""
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, "账号激活成功！请登录。")
        return redirect("login")
    else:
        messages.error(request, "激活链接无效或已过期。")
        return redirect("login")

def login_view(request):
    """用户登录"""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            # 仅数字验证码
            input_code = form.cleaned_data['captcha']
            session_code = request.session.get('captcha_code', '')
            if session_code != input_code:
                form.add_error("captcha", "验证码错误！")
                _refresh_captcha(request)
                return render(request, "registration/login.html", {"form": form})

            username_or_email = form.cleaned_data['username']
            password = form.cleaned_data['password']

            # 如果输入的是邮箱，则获取对应用户名
            if re.match(r"[^@]+@[^@]+\.[^@]+", username_or_email):
                try:
                    user_by_email = User.objects.get(email=username_or_email)
                    username_or_email = user_by_email.username
                except User.DoesNotExist:
                    form.add_error(None, "该邮箱未注册")
                    _refresh_captcha(request)
                    return render(request, "registration/login.html", {"form": form})

            user = authenticate(request, username=username_or_email, password=password)
            if user and user.is_active:
                login(request, user)
                return redirect("novel_list")  # 登录成功后进入主页index.html
            else:
                form.add_error(None, "用户名或密码错误或账户未激活")

            _refresh_captcha(request)
            return render(request, "registration/login.html", {"form": form})
    else:
        _refresh_captcha(request)
        form = LoginForm()
    return render(request, "registration/login.html", {"form": form})

def logout_view(request):
    """退出登录"""
    logout(request)
    return redirect("login")

def captcha_image(request):
    """返回数字验证码图片"""
    image, code = _generate_captcha()
    request.session['captcha_code'] = code
    buffer = BytesIO()
    image.save(buffer, format='PNG')
    return HttpResponse(buffer.getvalue(), content_type='image/png')

def _refresh_captcha(request):
    image, code = _generate_captcha()
    request.session['captcha_code'] = code


def _generate_captcha():
    """生成仅数字的验证码，长度4位"""
    code = ''.join(str(random.randint(0, 9)) for _ in range(4))
    image = Image.new('RGB', (80, 30), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text((10, 5), code, font=font, fill=(random.randint(0, 100), random.randint(0, 100), random.randint(0, 100)))
    return image, code
