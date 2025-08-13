# users/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import User, Province, City
from .serializers import (
    SignupSerializer, SetLocationSerializer, CreateCardSerializer,
    LoginSerializer, UpdateMeSerializer, MannerUpdateSerializer,
    ProvinceSerializer, CitySerializer, UserReadSerializer
)

DEMO_USER_ID = 1  # 게스트용

@api_view(["POST"])
def guest_login(request):
    request.session["user_id"] = DEMO_USER_ID
    return Response({"user_id": DEMO_USER_ID, "mode": "guest"})

def current_user_id(request):
    return request.session.get("user_id") or DEMO_USER_ID

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
    if "province_id" in s.validated_data:
        u.province_id = s.validated_data["province_id"]
    if "city_id" in s.validated_data:
        u.city_id = s.validated_data["city_id"]
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
    s = LoginSerializer(data=request.data)
    s.is_valid(raise_exception=True)
    if s.validated_data.get("username"):
        u = get_object_or_404(User, username=s.validated_data["username"])
    else:
        u = get_object_or_404(User, email=s.validated_data["email"])
    request.session["user_id"] = u.id
    return Response({"user_id": u.id})


@api_view(["POST"])
def logout(request):
    request.session.flush()
    return Response({"ok": True})

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

# ---------- 위치 ----------
@api_view(["GET"])
def list_provinces(_request):
    provinces = Province.objects.all()
    return Response({"data": ProvinceSerializer(provinces, many=True).data})


@api_view(["GET"])
def list_cities(request):
    pid = request.GET.get("province_id")
    qs = City.objects.filter(province_id=pid) if pid else City.objects.all()
    return Response({"data": CitySerializer(qs, many=True).data})

# ---------- 프로필 상세 ----------
def _mask(v, head=2, tail=2):
    if not v:
        return None
    if len(v) <= head + tail:
        return "*" * len(v)
    return v[:head] + "*" * (len(v) - (head + tail)) + v[-tail:]


@api_view(["GET"])
def profile_detail(request, user_id):
    viewer_id = current_user_id(request)
    u = get_object_or_404(User, id=user_id)
    data = {
        "id": u.id,
        "name": u.name,
        "avatar_url": u.avatar_url,
        "gender": u.gender,
        "age_band": u.age_band,
        "intro": u.intro,
    }
    if viewer_id == u.id:
        data["email"] = u.email
        data["phone"] = u.phone
        data["connection_status"] = "CONNECTED"
    else:
        data["masked_email"] = _mask(u.email)
        data["masked_phone"] = _mask(u.phone)
        data["connection_status"] = "NONE"
    return Response(data)