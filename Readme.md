JIRA like app backend

## What’s this project?

- Project to develop a technical understanding of the front and server-side sequence of processes using Django framework and React .

### 環境づくり

- Anaconda Navigator かなんかで雑に環境作っておくと良いかも
- Django で rest framework 使う際の install (pip)しておくもの
  (version はよしなに)

```
pip install Django==3.1
djangorestframework==3.11.1 -> RESTframework
django-cors-headers==3.4.0 -> ?
djangorestframework-simplejwt==4.6.0 -> json web token扱うよう
djoser==2.0.3 -> 認証関係のサードパーティ
 Pillow   -> アバター関係
```

### PyCharm を使う

- What’s Pycharm

  - チェコの JetBrains（ジェットブレインズ）が提供している IDE
  - Python 専用の IDE→Python の Web 開発フレームワークとの相性がとても良い

- Anaconda の仮想環境と紐付ける

  - preference から python の interpreter を設定(User/opt/anaconda3/envs/{作った環境}/bin/python)

- Django のプロジェクトを作る

  - `django-admin startproject {name} {directoryPATH} ` -> プロジェクト部分
    - project は以下の manage.py を実行(run server)するとプロジェクト立ち上がる
  - ` django-admin startapp {name}` -> api 部分

- ${project}/setting.py の修正

```
./jira_api/
├── __init__.py
├── __pycache__
├── asgi.py
├── settings.py
├── urls.py
└── wsgi.py
```

- 最初にインストールした諸々を設定する
- INSTALLED_APPに追記 →Djangoインスタンスの中で有効化されているすべてのDjangoアプリケーションの名前を保持するリストの環境変数→つまりそのままアプリの構成になる
- いつ追記する？
    - django-admin startapp でローカルアプリケーションを追加した場合, サードパーティのライブラリをインストールした場合→追記順に関してはバラバラ？らしい

```
'corsheaders',→ サードパティ
'rest_framework',→ サードパティ
'api.apps.ApiConfig', →ローカルのapp
'djoser’, → サードパティ
```

- Midleware に追記
  `corsheaders.middleware.CorsMiddleware,`
- ちなみに CORS(Cross-Origin Resource Sharing)とは - オリジン間の制限を変更することで、別オリジン間の HTTP リクエストを許可したりしなかったりする仕組み
  オリジンとは、「プロトコル」+「ホスト」+「ポート番号」の組み合わせのこと。上記の例でいうと

| サーバー | プロトコル | ホスト    | ポート番号 |
| -------- | ---------- | --------- | ---------- |
| React    | http       | localhost | 3000       |
| Django   | http       | localhost | 8000       |

-> Django の文脈で  Middleware  とは、Django のリクエスト/レスポンス処理にフックを加えるためのフレームワーク。Django の入力あるいは出力をグローバルに置き換えるための、軽量で低レベルの「プラグイン」システムで

- リクエストが送られた時に行う処理
- レスポンスを返す前に行う処理
  をフックとして持たせるみたいなイメージ

White list に追加

```python
CORS_ORIGIN_WIHITELIST = [
    "http://localhost:3000" -> reactの場合
]
```

- Permission 諸々の設定(JWT(JSON Web Token)活用 -> 署名、暗号化、URL-safe)

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated', -> プロジェクトの全体に新章地味のユーザーのみアクセスできるようにしている
    ],
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication', -> 認証にJWTを使う
    ],
}

SIMPLE_JWT = {
    'AUTH_HEADER_TYPES': ('JWT',),
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=30),
}

```

- その他
  - タイムゾーン変更
    - UTC -> Asia／Tokyo
  - 画像データ等の格納場所の指定

```python
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') -> BASE_DIRは大元のPATH(今回はjira_api)
MEDIA_URL = '/media/'
```

### {project}/urls に api や jwt の path をかく

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls), -> デフォルトはこれ
    path('api/', include('api.urls')),  -> api を叩いた時にapi/urlsに記載されたところに取りに行く
    path('authen/', include('djoser.urls.jwt')), -> dioserに取りに行く
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)　-> 画像諸々の保管庫
```

- api/urls の中身

```python
from django.urls import path, include
from rest_framework import routers
router = routers.DefaultRouter() -> routerを登録

urlpatterns = [
    path('', include(router.urls)),　-> viewとの紐付け, 追記していく
]

```

### Model 作成->よしなに

```python
from django.db import models
from django.contrib.auth.models import User　＃Djangoにあるuserモデル
from django.core.validators import MinValueValidator
import uuid #128bitの一意なキー

#拡張子と連結
def upload_avatar_path(instance, filename):
    ext = filename.split('.')[-1]
    return '/'.join(['avatars', str(instance.user_profile.id) + str(".") + str(ext)])


class Profile(models.Model):
    user_profile = models.OneToOneField(
        User, related_name='user_profile',
        on_delete=models.CASCADE #Cascade設定するとusr消去された時に一緒に消去される
    )
    img = models.ImageField(blank=True, null=True, upload_to=upload_avatar_path)

    def __str__(self):
        return self.user_profile.username


class Category(models.Model):
    item = models.CharField(max_length=100)

    def __str__(self):
        return self.item


class Task(models.Model):
    STATUS = (
        ('1', 'Not started'),
        ('2', 'On going'),
        ('3', 'Done'),
    )
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    task = models.CharField(max_length=100)
	category = models.ForeignKey(Category, on_delete=models.CASCADE) #外部キー制約は.ForeignKey
 	…. # 略


    def __str__(self):
        return self.task

```

- migration する
  マイグレーションは Django がモデル (そしてデータベーススキーマでもあります) の変更を保存する方法
  流れ

* モデルを変更する (models.py  の中の)
* これらの変更のためのマイグレーションを作成するために  python manage.py makemigrations  を実行
* データベースにこれらの変更を適用するために  python manage.py migrate  を実行

```
$ python manage.py makemigrations
Migrations for 'api':
  api/migrations/0001_initial.py
    - Create model Category
    - Create model Task
    - Create model Profile

$python manage.py migrate      -> migrationする
Operations to perform:
  Apply all migrations: admin, api, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying admin.0001_initial... OK
  Applying admin.0002_logentry_remove_auto_add... OK


```

### Admin から生成したモデルを見る

admin.py に追加したモデルを登録

```python
from django.contrib import admin
from .models import Category, Task, Profile

admin.site.register(Category)
admin.site.register(Task)
admin.site.register(Profile)

```

server を起動してhttp://127.0.0.1:8000//admin にアクセス（login に user が必要)
` $ python manage.py createsuperuser`

GUI からオブジェクトの追加や消去が簡単にできる

## Selielizer -> データの入出力を扱い、モデルへの橋渡しをするクラス

例えば)フロント →Django→DB に Get のリクエストが来た場合どんな Json を返すかを決める

```python
from rest_framework import serializers
from .models import Task,Category,Profile
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta: #Metaの部分に具体的な設定を書く
        model = User #使いたいモデル
        fields = ['id','username','password'] #使いたいフィールド
        extra_kwargs = {'password':{'write_only': True, 'required': True}} #特定のパラメータに関してのオプション設定

    def create(self, validated_data): #user selielizerに関してはパスワードをハッシュ科するためにcreateメソッドをオーバライドする
        user = User.objects.create_user(**validated_data) #validateする
        return user
….

‘’’
Foreignkeyを使って別のモデルを参照している場合→primarykeyの番号のみが返される→しかしフロントからは文字列も見たいなどの場合があるのでitemを結合して返すようにする
Ex)category_item = serializers.ReadOnlyField(source='category.item', read_only=True)
‘’’
class TaskSerializer(serializers.ModelSerializer):
    category_item = serializers.ReadOnlyField(source='category.item', read_only=True)
    owner_username = serializers.ReadOnlyField(source='owner.username', read_only=True)
    responsible_username = serializers.ReadOnlyField(source='responsible.username', read_only=True)
    status_name = serializers.CharField(source='get_status_display', read_only=True)
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    updated_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)

    class Meta:
        model = Task
        fields = ['id', 'task', 'description', 'criteria', 'status', 'status_name', 'category', 'category_item',
                  'estimate','responsible','responsible_username','owner','owner_username', 'created_at','updated_at']
        extra_kwargs = {'owner': {'read_only': True}}


```

## views の作成

Django でいうビュー(view)はページがリクエストされたときにサーバー内でどのような処理をするかを記述したもの

ex)データベースの操作やどのような要素をページに含めるか、などの記述

```python
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

```

### views と urls を紐付けてエンドポイントを完成させる

api/urls

```python
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
```

### 動作確認

- Postman 使えば楽
- Access トークンの取得の際は`/authen/jwt/create/`を叩く
  - Chrome の拡張機能の modheader に accesstoken 持たせると認証突破できる


### AWSへのデプロイ
- AWS上で扱う際に便利なパッケージ 
  - 環境変数,DBを簡単に扱えるようにする
```bash
$ pip install django-environ 
$ pip install dj-database-url
```
- setting.pyの設定

adminの画面とかもともとデフォルトであったものをstaticにまとめるためにRootを設定
```python
STATIC_ROOT = os.path.join(BASE_DIR, 'static')
```
ベタ書きだった部分をenvファイルから読み込む
```python
import environ
env = environ.Env()
env.read_env(os.path.join(BASE_DIR,'.env'))
SECRET_KEY = env('SECRET_KEY')
DEBUG = env('DEBUG')
DATABASES = {
    'default': env.db(),
}
```

- .env
↓よしなに
```
SECRET_KEY=-----
DEBUG=False
DATABASE_URL=sqlite://db.splite3
```
- 仮想環境に入れてた依存関係等々を掃き出しとく
` pip freeze > requirements-dev.txt`
  
- requiements.txtを作って依存関係のやつとその他prod環境で使いたいものを入れる
```
-r requirements-dev.txt
gunicorn
psycopg2
```



