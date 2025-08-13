from django.urls import path
from .views import graph

urlpatterns = [
    path("graph", graph),  # GET /network/graph?depth=1|2
]
