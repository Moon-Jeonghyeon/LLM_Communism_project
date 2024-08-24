from django.shortcuts import render, redirect

def main_page(request):
    # # 로그인 되어 있는 경우, 메인 페이지로 리다이렉트
    if request.user.is_authenticated:
        return render(request, "main.html")

    # 로그인되어 있지 않은 경우, 로그인 페이지로 리다이렉트
    else:
        return redirect("/users/login/")

