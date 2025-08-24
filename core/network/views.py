# network/views.py (수정된 최종 버전)

from rest_framework.decorators import api_view   # <-- 추가
from rest_framework.response import Response     # <-- 추가
from django.shortcuts import get_object_or_404

from users.models import User
from .models import Friendship
from users.views import current_user_id          # <-- users 앱에서 current_user_id 함수를 가져옵니다.


@api_view(["GET"])  # <-- 함수를 API 뷰로 만들어주는 데코레이터 추가
def graph(request):
    """
    GET /network/graph?depth=1|2
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
    
    users = User.objects.filter(id__in=user_ids).only("id", "name", "avatar_url", "intro")
    nodes = [{"id": u.id, "name": u.name, "avatar_url": u.avatar_url, "intro": u.intro} for u in users]

    return Response({"center": me, "nodes": nodes, "edges": edges}) # <-- Response 객체로 반환