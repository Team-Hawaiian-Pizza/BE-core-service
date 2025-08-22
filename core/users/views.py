from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User
from .serializers import *

DEMO_USER_ID = 1  # 게스트용


def current_user_id(request):
    # 1) 헤더 우선
    xuid = request.headers.get("User-Id")
    if xuid and str(xuid).isdigit():
        return int(xuid)
    # 2) 쿼리스트링/바디 보조
    q = request.GET.get("user_id") or request.POST.get("user_id")
    if q and str(q).isdigit():
        return int(q)
    # 3) 기본값(게스트)
    return DEMO_USER_ID

# ---------- 회원가입 ----------
@api_view(["POST"])
def signup(request):
    s = SignupSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    u = User.objects.create(
        username=s.validated_data["username"],
        name=s.validated_data.get("name") or s.validated_data["username"],
        email=s.validated_data.get("email", "")
    )
    return Response({"user_id": u.id})

@api_view(["POST"])
def set_location(request):
    s = SetLocationSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    u = get_object_or_404(User, id=s.validated_data["user_id"])
    if "province_name" in s.validated_data: u.province_name = s.validated_data["province_name"]
    if "city_name" in s.validated_data:     u.city_name     = s.validated_data["city_name"]
    u.save()
    return Response({"ok": True})

@api_view(["POST"])
def create_card(request):
    s = CreateCardSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    u = get_object_or_404(User, id=s.validated_data["user_id"])
    for field, value in s.validated_data.items():
        if field != "user_id":
            setattr(u, field, value)
    u.save()
    return Response({"ok": True})

# ---------- 로그인/로그아웃 ----------
@api_view(["POST"])
def login(request):
    # username 또는 email로 사용자 조회만 해주고 id를 내려줌(세션 저장 없음)
    s = LoginSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    if s.validated_data.get("username"):
        u = get_object_or_404(User, username=s.validated_data["username"])
    else:
        u = get_object_or_404(User, email=s.validated_data["email"])
    return Response({"user_id": u.id, "mode": "demo"})


# ---------- 내 정보 ----------
@api_view(["GET"])
def me(request):
    u = get_object_or_404(User, id=current_user_id(request))
    return Response(UserReadSerializer(u).data)

@api_view(["PATCH"])
def update_me(request):
    s = UpdateMeSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    u = get_object_or_404(User, id=current_user_id(request))
    for field, value in s.validated_data.items():
        setattr(u, field, value)
    u.save()
    return Response({"ok": True})

@api_view(["PUT"])
def update_manner(request):
    s = MannerUpdateSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    u = get_object_or_404(User, id=current_user_id(request))
    u.manner_temperature = s.validated_data["manner_temperature"]
    u.save()
    return Response({"ok": True})

# ---------- 프로필 상세 ----------
def _mask(v, head=2, tail=2):
    if not v: return None
    if len(v) <= head + tail: return "*" * len(v)
    return v[:head] + "*" * (len(v) - (head + tail)) + v[-tail:]

@api_view(["GET"])
def profile_detail(request, user_id):
    viewer_id = current_user_id(request)
    u = get_object_or_404(User, id=user_id)
    data = {
        "id": u.id, "name": u.name, "avatar_url": u.avatar_url,
        "gender": u.gender, "age_band": u.age_band, "intro": u.intro,
        "province_name": u.province_name, "city_name": u.city_name,
    }
    if viewer_id == u.id:
        data["email"] = u.email; data["phone"] = u.phone; data["connection_status"] = "CONNECTED"
    else:
        data["masked_email"] = _mask(u.email)
        data["masked_phone"] = _mask(u.phone)
        data["connection_status"] = "NONE"
    return Response(data)

# ---------- 전체 유저 ----------
@api_view(["GET"])
def list_users(request):
    qs = User.objects.all().order_by("-id")  # 최신 가입 순
    data = UserReadSerializer(qs, many=True).data
    return Response({"count": len(data), "results": data})