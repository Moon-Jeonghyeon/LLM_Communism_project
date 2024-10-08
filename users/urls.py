from django.urls import path
from users import views
from django.conf.urls.static import static
from django.conf import settings

app_name = "users"
urlpatterns = [
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("signup/", views.signup, name="signup"),
    path("memo/", views.memo, name="memo"),
    path("memo/delete/<int:memo_id>/", views.delete_memo, name="delete_memo"),
    path("edit/<int:memo_id>/", views.edit_memo, name="edit_memo"),
    path("profile/<int:user_id>/", views.profile, name="profile"),
    path("edit/<str:field>/", views.profile_edit, name="profile_edit"),
]
