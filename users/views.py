from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from users.forms import LoginForm, SignupForm
from users.models import User

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