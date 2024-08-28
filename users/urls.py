from django.urls import path
from users import views

app_name = "users"
urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup, name="signup"),
    path("memo/", views.memo, name="memo"),
    path("profile/<int:user_id>/", views.profile, name="profile"),
    path("edit/<str:field>/", views.profile_edit, name="profile_edit"),
]