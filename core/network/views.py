# network/views.py
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import User
from .models import Friendship

DEMO_USER_ID = 1  # 기본(게스트)

def current_user_id(request):
    # 1) 헤더(User-Id) 우선
    xuid = request.headers.get("User-Id")
    if xuid and str(xuid).isdigit():
        return int(xuid)
    # 2) 쿼리스트링 보조 (?user_id=)
    q = request.GET.get("user_id") or request.POST.get("user_id")
    if q and str(q).isdigit():
        return int(q)
    # 3) 기본값
    return DEMO_USER_ID

def graph(request):
    """
    GET /network/graph?depth=1|2&user_id=<옵션>
    응답: { center, nodes:[{id,name,avatar_url?,intro?}], edges:[{source,target}] }
    """
    me = current_user_id(request)
    depth = int(request.GET.get("depth", 2))

    # 1차 친구
    f1_ids = list(Friendship.objects.filter(a_id=me).values_list("b_id", flat=True))
    user_ids = {me, *f1_ids}
    edges = [{"source": me, "target": uid} for uid in f1_ids]

    # 2차 친구(옵션)
    if depth >= 2 and f1_ids:
        f2 = Friendship.objects.filter(a_id__in=f1_ids).values_list("a_id", "b_id")
        for a_id, b_id in f2:
            if b_id not in user_ids:  # me/1차 제외
                user_ids.add(b_id)
                edges.append({"source": a_id, "target": b_id})
    
    # 1. DB에서 user 정보를 가져올 때 'intro' 필드를 추가로 요청합니다.
    users = User.objects.filter(id__in=user_ids).only("id", "name", "avatar_url", "intro")
    
    # 2. 응답 데이터(nodes)를 만들 때 'intro' 필드를 추가합니다.
    nodes = [{"id": u.id, "name": u.name, "avatar_url": u.avatar_url, "intro": u.intro} for u in users]

    return Response({"center": me, "nodes": nodes, "edges": edges})