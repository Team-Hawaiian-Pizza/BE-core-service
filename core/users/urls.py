# users/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    # 회원가입 플로우
    path("signup", signup),                    # POST
    path("signup/location", set_location),     # POST
    path("signup/card", create_card),          # POST

    # 로그인/로그아웃
    path("login", login),                      # POST
    path("logout", logout),                    # POST
    path("guest-login", guest_login),

    # 내 정보
    path("me", me),                            # GET
    path("me/update", update_me),              # PATCH
    path("me/manner", update_manner),          # PUT

    # 지역
    path("locations/si-do", list_provinces),   # GET
    path("locations/si-gun-gu", list_cities),  # GET ?province_id=

    # 프로필 상세
    path("profiles/<int:user_id>", profile_detail),  # GET
]
