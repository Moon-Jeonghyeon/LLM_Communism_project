from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect, get_object_or_404
from users.forms import LoginForm, SignupForm
from users.models import User
from words.models import Memo
import re
from django.contrib import messages
from django.http import HttpResponse


# Create your views here.
def login_view(request):
    # 이미 로그인되어 있는 경우
    if request.user.is_authenticated:
        return redirect("/")
    
    if request.method == "POST":
        # LoginForm 인스턴스를 만들며, 입력 데이터는 request.POST 를 사용
        form = LoginForm(data=request.POST)

        # # LoginForm 에 들어온 데이터가 적절한지 유효성 검사
        # print("form.is_valid(): ", form.is_valid())

        # # 유효성 검사 이후에는 cleaned_data 에서 데이터를 가져와 사용
        # print("form.cleaned_data: ", form.cleaned_data)
        # return render(request, "user/login.html", {"form": form})

        # LoginForm 에 전달된 데이터가 유효하다면
        if form.is_valid():
            # username과 password 값을 가져와 변수에 할당
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # username, password 에 해당하는 사용자가 있는지 검사
            user = authenticate(username=username, password=password)

            # 해당 사용자가 존재한다면
            if user:
                # 로그인 처리 후, 피드 페이지로 리다이렉트
                login(request, user)
                return redirect("/")
            
            # 해당 사용자가 없다면 form에 에러 추가
            else:
                form.add_error(None, "입력한 자격증명에 해당하는 사용자가 없습니다")

        # 어떤 이유든, 실패한 경우라면 다시 LoginForm 을 사용한 로그인 페이지 렌더링
        return render(request, "users/login.html", {"form": form})
    
    else:
        # LoginForm 인스턴스를 생성
        form = LoginForm()

        # 생성한 LoginForm 인스턴스를 템플릿에 "form" 이라는 키로 전달
        return render(request, "users/login.html", {"form": form})
    
def logout_view(request):
    # logout 함수 호출에 request를 전달
    logout(request)

    # logout 처리 후, 로그인페이지로 이동
    return redirect("/users/login/")

def signup(request):
    if request.method == "POST":
        form = SignupForm(data=request.POST, files=request.FILES)

        # Form에 에러가 없다면 form의 save() 메서드로 사용자를 생성
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect("/")

    # GET 요청에서는 빈 Form을 보여줌
    else:
        # SignupForm 인스턴스를 생성, Template에 전달
        form = SignupForm()

    context = {"form": form}
    return render(request, "users/signup.html", context)

def memo(request):
    # 최근 작성된 글이 위로 오도록 내림차순 정렬
    memos = Memo.objects.all().order_by('-created_at')

    # 수정할 메모를 가져옴
    edit_memo_id = request.GET.get('edit_memo_id')
    edit_memo = None

    # 수정할 메모 아이디를 가져온 경우 덮어쓰기
    if edit_memo_id:
        edit_memo = get_object_or_404(Memo, id=edit_memo_id, user=request.user)

    # POST 요청 시
    if request.method == "POST":
        content = request.POST["content"]
        memo_id = request.POST.get("memo_id")

        if memo_id:
            # 기존 메모 수정
            memo = get_object_or_404(Memo, id=memo_id, user=request.user)
            memo.content = content
            memo.save()
        else:
            # 새 메모 생성
            memo = Memo.objects.create(content=content, user=request.user)
            memo.save()
        
        return redirect("/users/memo/")
    
    context = {
        "memos": memos,
        "edit_memo": edit_memo,
    }

    return render(request, "users/memo.html", context)

def delete_memo(request, memo_id):
    memo = get_object_or_404(Memo, id=memo_id, user=request.user)

    if request.method == "POST":
        memo.delete()
        return redirect("/users/memo/")
    
    return HttpResponse(status=405)

def edit_memo(request, memo_id):
    # 수정할 Todo 객체를 가져오고, 없다면 404 에러 반환
    memo = get_object_or_404(Memo, id=memo_id)

    if request.method == "POST":
        # list나 category 값이 없으면 원래 값을 그대로 사용
        memo.content = request.POST.get("content", memo.content)
        memo.save()
        return redirect("/users/memo/")
    
    # GET 요청 시 기존 데이터와 함께 수정 페이지 렌더링
    return render(request, "users/edit_memo.html", {"memo": memo})

def profile(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)

    # 요청을 보낸 사용자가 프로필 사용자가 아닐 때
    if request.user.is_authenticated and profile_user != request.user:
        # 팔로우 여부 확인
        pass

    context = {
        "profile_user": profile_user,
    }

    return render(request, "users/profile.html", context)

def profile_edit(request, field):
    # 사용자가 로그인된 상태가 아니라면 로그인 페이지로 리다이렉트
    if not request.user.is_authenticated:
        return redirect('/user/login/')
    
    profile_user = request.user

    # POST 요청 시
    if request.method == "POST":
        # field가 profile_image일 때
        if field == "profile_image":
            profile_user.profile_image = request.FILES.get("profile_image")

        # field가 nickname일 때
        elif field == "name":
            profile_user.name = request.POST.get("name", profile_user.name)

        # field가 email일 때
        elif field == "email":
            profile_user.email = request.POST.get("email", profile_user.email)
            email_regex = re.compile(r'^[a-zA-Z0-9+-_.]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$')

            if not email_regex.search(profile_user.email):
                messages.warning(request, "Incorrect email address.")
                return redirect("users:profile", user_id=profile_user.id)
            

        # field에 이외 잘못된 값이 들어갔을 때, 프로필 페이지로 리다이렉트
        else:
            return redirect("users:profile", user_id=profile_user.id)
        
        profile_user.save()
        # 수정된 내용을 반영한 후 리다이렉트
        return redirect("users:profile", user_id=profile_user.id)
    
    # GET 요청 시 기존 데이터와 함께 수정 폼 호출
    return render(request, "users:profile_edit", {"profile_user": profile_user})
