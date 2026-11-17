
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    health_check,
    business_list,
    shop_list,
    category_list,
    product_list,
    stock_list,
    sale_confirm,
)

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("auth/token/", obtain_auth_token, name="obtain-auth-token"),
    path("businesses/", business_list, name="business-list"),
    path(
        "businesses/<uuid:business_id>/shops/",
        shop_list,
        name="shop-list",
    ),
    path(
        "businesses/<uuid:business_id>/categories/",
        category_list,
        name="category-list",
    ),
    path(
        "businesses/<uuid:business_id>/products/",
        product_list,
        name="product-list",
    ),
    path(
        "businesses/<uuid:business_id>/shops/<uuid:shop_id>/stock/",
        stock_list,
        name="stock-list",
    ),
    path(
        "businesses/<uuid:business_id>/sales/confirm/",
        sale_confirm,
        name="sale-confirm",
    ),
]
