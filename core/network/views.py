from rest_framework.decorators import api_view
from rest_framework.response import Response
from users.models import User
from .models import Friendship

DEMO_USER_ID = 1

def current_user_id(request):
    xuid = request.headers.get("User-Id")
    if xuid and str(xuid).isdigit():
        return int(xuid)
    q = request.GET.get("user_id")
    if q and str(q).isdigit():
        return int(q)
    return DEMO_USER_ID

@api_view(["GET"])   
def graph(request):
    me = current_user_id(request)
    depth = int(request.GET.get("depth", 2))

    f1_ids = list(Friendship.objects.filter(a_id=me).values_list("b_id", flat=True))
    user_ids = {me, *f1_ids}
    edges = [{"source": me, "target": uid} for uid in f1_ids]

    if depth >= 2 and f1_ids:
        for a_id, b_id in Friendship.objects.filter(a_id__in=f1_ids).values_list("a_id", "b_id"):
            if b_id not in user_ids:
                user_ids.add(b_id)
                edges.append({"source": a_id, "target": b_id})

    users = User.objects.filter(id__in=user_ids).only("id", "name", "avatar_url")
    nodes = [{"id": u.id, "name": u.name, "avatar_url": u.avatar_url} for u in users]

    return Response({"center": me, "nodes": nodes, "edges": edges})
