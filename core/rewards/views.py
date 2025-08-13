from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.conf import settings
from .models import Brand, StampBoard, Coupon

def current_user_id(request):
    return request.session.get("user_id") or getattr(settings, "DEMO_USER_ID", 1)

# --- (선택) 브랜드 목록: 스탬프/쿠폰 화면 상단용 ---
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

    # 다 채우면 쿠폰 발급(자동)
    if board.filled == board.total:
        brand = board.brand
        Coupon.objects.create(
            user_id=me, brand=brand,
            title=f"{brand.name} 무료 쿠폰",
            image=brand.hero_image
        )
    return Response({"filled": board.filled, "total": board.total})

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
