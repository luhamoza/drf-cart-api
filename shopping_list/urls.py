from django.urls import path, include
from rest_framework import routers
from shopping_list.api.viewsets import ShoppingItemViewsets

router = routers.DefaultRouter()
router.register("shopping-items", ShoppingItemViewsets, basename="shopping-items")

urlpatterns = [
    path("api/", include(router.urls))
]