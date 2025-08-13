from django.urls import path
from .views import my_code, issue, enter_code, inbound_requests, accept, reject

urlpatterns = [
    path("my-code", my_code),                # GET
    path("issue", issue),                    # POST
    path("enter-code", enter_code),          # POST {code}
    path("requests", inbound_requests),      # GET
    path("accept/<int:req_id>", accept),     # POST
    path("reject/<int:req_id>", reject),     # POST
]
