from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, CategoryViewSet

router = DefaultRouter()

router.register(r"notes", NoteViewSet, basename="note")
router.register(r"categories", CategoryViewSet, basename="category")

urlpatterns = [
    path("", include(router.urls)),
]