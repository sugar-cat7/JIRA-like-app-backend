from django.urls import path, include
from rest_framework import routers
from .views import TaskViewSet, CategoryViewSet, CreateUserView, ListUserView, LoginUserView, ProfileViewSet
#viewsの方でmodelviewを継承したものとgenericsを継承したもので記述が違う
#modelviewはこっち
router = routers.DefaultRouter()
router.register('category', CategoryViewSet)
router.register('tasks', TaskViewSet)
router.register('profile', ProfileViewSet)
#genericsはこっち
urlpatterns = [
    path('create/', CreateUserView.as_view(), name='create'),
    path('users/', ListUserView.as_view(), name='users'),
    path('loginuser/', LoginUserView.as_view(), name='loginuser'),
    path('', include(router.urls)),
]