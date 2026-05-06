"""
urls.py — students app URL patterns
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegisterView, MeView, StudentRecordViewSet

router = DefaultRouter()
router.register(r'student-records', StudentRecordViewSet, basename='studentrecord')

urlpatterns = [
    # User management
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),
    # Student records (CRUD)
    path('', include(router.urls)),
]
