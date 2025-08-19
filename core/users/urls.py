from django.urls import path
from .views import *

urlpatterns = [
    # 회원가입 플로우
    path("signup", signup),                    # POST
    path("signup/location", set_location),     # POST
    path("signup/card", create_card),          # POST

    # 로그인/로그아웃
    path("login", login),                      # POST
    path("guest-login", guest_login),          # POST
    path("logout", logout),                    # POST

    # 내 정보
    path("me", me),                            # GET
    path("me/update", update_me),              # PATCH
    path("me/manner", update_manner),          # PUT

    # 프로필 상세
    path("profiles/<int:user_id>", profile_detail),  # GET
    path("all", list_users),    # GET
]
