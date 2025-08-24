# rewards/views.py
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Brand, StampBoard, Coupon

DEMO_USER_ID = 1  # 게스트 기본 ID

def current_user_id(request):
    # 1) 헤더(User-Id)
    xuid = request.headers.get("User-Id")
    if xuid and str(xuid).isdigit():
        return int(xuid)
    # 2) 쿼리스트링/바디
    q = request.GET.get("user_id") or request.POST.get("user_id")
    if q and str(q).isdigit():
        return int(q)
    # 3) 기본
    return DEMO_USER_ID

# --- 브랜드 목록 ---
@api_view(["GET"])
def list_brands(_request):
    data = [{"id": b.id, "name": b.name, "image": b.hero_image, "benefit": b.benefit_text}
            for b in Brand.objects.all()]
    return Response({"data": data})

# --- 스탬프 ---
@api_view(["GET"])
def get_stamp(request, brand_id):
    me = current_user_id(request)
    board, _ = StampBoard.objects.get_or_create(user_id=me, brand_id=brand_id)
    return Response({"brand_id": brand_id, "total": board.total, "filled": board.filled})

@api_view(["POST"])
def punch_stamp(request, brand_id):
    me = current_user_id(request)
    board, _ = StampBoard.objects.get_or_create(user_id=me, brand_id=brand_id)
    if board.filled >= board.total:
        return Response({"already_full": True})
    board.filled += 1
    board.save()

    # 다 채우면 쿠폰 발급
    if board.filled == board.total:
        brand = board.brand
        Coupon.objects.create(
            user_id=me, brand=brand,
            title=f"{brand.name} 무료 쿠폰",
            image=brand.hero_image
        )
    return Response({"filled": board.filled, "total": board.total})

@api_view(["GET"])
def list_all_stamps(request):
    """
    현재 사용자가 보유한 모든 스탬프판 목록을 반환합니다.
    """
    me = current_user_id(request)
    
    # 현재 사용자의 모든 스탬프보드를 가져옵니다.
    # select_related('brand')를 사용해 브랜드 정보도 함께 조회하여 DB 효율을 높입니다.
    stamp_boards = StampBoard.objects.filter(user_id=me).select_related("brand").order_by("id")
    
    # API 응답 형식에 맞게 데이터를 가공합니다.
    data = []
    for board in stamp_boards:
        data.append({
            "brand_id": board.brand.id,
            "brand_name": board.brand.name,
            "brand_image": board.brand.hero_image,
            "total": board.total,
            "filled": board.filled,
        })
        
    return Response({"data": data})

# --- 쿠폰 ---
@api_view(["GET"])
def list_coupons(request):
    me = current_user_id(request)
    qs = Coupon.objects.filter(user_id=me).select_related("brand").order_by("-id")
    data = []
    for c in qs:
        data.append({
            "id": c.id,
            "title": c.title,
            "brand": c.brand.name,
            "image": c.image,
            "expires_at": c.expires_at,
            "used": bool(c.used_at),
        })
    return Response({"data": data})

@api_view(["POST"])
def use_coupon(request, coupon_id):
    me = current_user_id(request)
    c = get_object_or_404(Coupon, id=coupon_id, user_id=me)
    if c.used_at:
        return Response({"already_used": True})
    if c.expires_at and c.expires_at < timezone.now():
        return Response({"expired": True})
    c.used_at = timezone.now()
    c.save()
    return Response({"ok": True})
