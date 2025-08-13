from django.urls import path
from .views import list_brands, get_stamp, punch_stamp, list_coupons, use_coupon

urlpatterns = [
    path("brands", list_brands),                 # GET
    path("stamps/<int:brand_id>", get_stamp),    # GET
    path("stamps/<int:brand_id>/punch", punch_stamp),  # POST
    path("coupons", list_coupons),               # GET
    path("coupons/<int:coupon_id>/use", use_coupon),   # POST
]
