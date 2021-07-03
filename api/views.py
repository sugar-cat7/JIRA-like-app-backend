from django.shortcuts import render
from rest_framework import status, permissions, generics, viewsets
from .serializers import UserSerializer, CategorySerializer, TaskSerializer, ProfileSerializer
from rest_framework.response import Response
from .models import Task, Category, Profile
from django.contrib.auth.models import User
from . import custompermissions

#エンドポイントの作成 新規ユーザ作成 api/create (POST)
class CreateUserView(generics.CreateAPIView):#generics CRUDのうち一部の機能に特化
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,) #JWTはユーザーがないときは必要ないので

#エンドポイントの作成　ユーザリスト取得 api/user (GET)
class ListUserView(generics.ListAPIView):#get　list に特化したものが用意されている
    queryset = User.objects.all()
    serializer_class = UserSerializer

#エンドポイントの作成 ログインユーザー取得 api/loginuser (GET)
class LoginUserView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user #ログインしているユーザーでオーバライドしておく

    def update(self, request, *args, **kwargs):
        response = {'message': 'PUT method is not allowed'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

#エンドポイントの作成 プロフィールの作成/更新 api/profile (POST/PUT)
class ProfileViewSet(viewsets.ModelViewSet): # ModelViewSet -> CRUDとか丸ごと提供されてる
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    #ログインユーザーのオブジェクトが作成されるようにする
    def perform_create(self, serializer):
        serializer.save(user_profile=self.request.user)

    def destroy(self, request, *args, **kwargs):
        response = {'message': 'DELETE method is not allowed'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        response = {'message': 'PATCH method is not allowed'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

#エンドポイントの作成 新規カテゴリ作成 api/profile (POST)
class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

    def destroy(self, request, *args, **kwargs):
        response = {'message': 'DELETE method is not allowed'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def update(self, request, *args, **kwargs):
        response = {'message': 'PUT method is not allowed'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

    def partial_update(self, request, *args, **kwargs):
        response = {'message': 'PATCH method is not allowed'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)

#タスクのCRUD
class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (permissions.IsAuthenticated, custompermissions.OwnerPermission,)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    def partial_update(self, request, *args, **kwargs):
        response = {'message': 'PATCH method is not allowed'}
        return Response(response, status=status.HTTP_400_BAD_REQUEST)