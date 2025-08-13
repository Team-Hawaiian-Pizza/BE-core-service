from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db import transaction
from django.conf import settings
from users.models import User
from .models import InviteCode, ConnectionRequest
from network.models import Friendship
import secrets

def current_user_id(request):
    return request.session.get("user_id") or getattr(settings, "DEMO_USER_ID", 1)

def issue_code_str():
    return secrets.token_urlsafe(6)[:8]  # 8자

# 1) 내 코드 조회(없으면 생성)
@api_view(["GET"])
def my_code(request):
    me_id = current_user_id(request)
    ic, created = InviteCode.objects.get_or_create(
        owner_id=me_id, defaults={"code": issue_code_str()}
    )
    return Response({"code": ic.code, "new": created})

# 2) 코드 재발급
@api_view(["POST"])
def issue(request):
    me_id = current_user_id(request)
    code = issue_code_str()
    InviteCode.objects.update_or_create(owner_id=me_id, defaults={"code": code})
    return Response({"code": code})

def _already_connected(a_id, b_id):
    return Friendship.objects.filter(a_id=a_id, b_id=b_id).exists() or \
           Friendship.objects.filter(a_id=b_id, b_id=a_id).exists()

# 3) 코드 입력 → 요청 생성
@api_view(["POST"])
def enter_code(request):
    me_id = current_user_id(request)
    code = (request.data.get("code") or "").strip()
    if not code:
        return Response({"error":"code_required"}, status=400)

    ic = get_object_or_404(InviteCode, code=code)
    if ic.owner_id == me_id:
        return Response({"error":"cannot_request_self"}, status=400)

    # ✅ 이미 친구면 요청 생성 안 함
    if _already_connected(me_id, ic.owner_id):
        return Response({"already_connected": True})

    # 기존 PENDING 재사용
    cr, created = ConnectionRequest.objects.get_or_create(
        from_user_id=me_id, to_user_id=ic.owner_id, status=ConnectionRequest.PENDING
    )
    return Response({"request_id": cr.id, "new": created})
# 4) 인바운드 요청 목록
@api_view(["GET"])
def inbound_requests(request):
    me_id = current_user_id(request)
    qs = (ConnectionRequest.objects
          .select_related("from_user")
          .filter(to_user_id=me_id, status=ConnectionRequest.PENDING)
          .order_by("-created_at"))
    data = [{"id": r.id,
             "from_user": {"id": r.from_user.id, "name": r.from_user.name, "username": r.from_user.username},
             "created_at": r.created_at} for r in qs]
    return Response({"data": data})

# 5) 수락
@api_view(["POST"])
def accept(request, req_id):
    me_id = current_user_id(request)
    r = get_object_or_404(ConnectionRequest, id=req_id, to_user_id=me_id)
    if r.status != ConnectionRequest.PENDING:
        return Response({"error":"already_processed"}, status=400)

    with transaction.atomic():
        # ✅ 양방향 edge 생성
        Friendship.objects.get_or_create(a_id=me_id, b_id=r.from_user_id)
        Friendship.objects.get_or_create(a_id=r.from_user_id, b_id=me_id)

        r.status = ConnectionRequest.ACCEPTED
        r.responded_at = timezone.now()
        r.save()

    return Response({"ok": True})

# 5-2) 거절
@api_view(["POST"])
def reject(request, req_id):
    me_id = current_user_id(request)
    r = get_object_or_404(ConnectionRequest, id=req_id, to_user_id=me_id)
    if r.status != ConnectionRequest.PENDING:
        return Response({"error":"already_processed"}, status=400)
    r.status = ConnectionRequest.REJECTED
    r.responded_at = timezone.now()
    r.save()
    return Response({"ok": True})
