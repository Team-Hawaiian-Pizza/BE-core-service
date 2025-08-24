from django.urls import path
from .views import *

urlpatterns = [
    path("brands", list_brands),                 # GET
    path("stamps/<int:brand_id>", get_stamp),    # GET
    path("stamps/<int:brand_id>/punch", punch_stamp),  # POST
    path("coupons", list_coupons),               # GET
    path("coupons/<int:coupon_id>/use", use_coupon),   # POST
    path("stamps/all", list_all_stamps), # GET
]
