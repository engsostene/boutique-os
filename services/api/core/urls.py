
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from .views import (
    health_check,
    business_list,
    shop_list,
    category_list,
    product_list,
    stock_list,
)

urlpatterns = [
    # Public endpoint: confirms the backend is alive.
    path("health/", health_check, name="health-check"),

    # Authentication: React exchanges username/password for a token.
    path("auth/token/", obtain_auth_token, name="obtain-auth-token"),

    # Business data: every private endpoint checks authentication
    # and business membership inside its corresponding view.
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
]
