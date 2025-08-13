from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.conf import settings
from users.models import User
from .models import Friendship

def current_user_id(request):
    return request.session.get("user_id") or getattr(settings, "DEMO_USER_ID", 1)

@api_view(["GET"])
def graph(request):
    """
    GET /network/graph?depth=1|2
    응답: { center, nodes:[{id,name,avatar_url?}], edges:[{source,target}] }
    """
    me = int(request.GET.get("user_id") or current_user_id(request))
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

    users = User.objects.filter(id__in=user_ids).only("id", "name", "avatar_url")
    nodes = [{"id": u.id, "name": u.name, "avatar_url": u.avatar_url} for u in users]

    return Response({"center": me, "nodes": nodes, "edges": edges})
