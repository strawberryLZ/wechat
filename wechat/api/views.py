import random
import uuid
import re
from datetime import datetime

from api.Myserializer import MySerializer
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.views import APIView
from rest_framework import serializers
from django_redis import get_redis_connection
from rest_framework.generics import ListAPIView, CreateAPIView,RetrieveAPIView
from rest_framework.filters import BaseFilterBackend
from api.MylimitPg.mylimit import OldBoyLimitPagination
from rest_framework import status
from utils import msg
from django.forms import model_to_dict
from api import models


def phone_validator(value):
    if not re.match(r"^(1[3|4|5|6|7|8|9])\d{9}$", value):
        raise ValidationError('手机格式错误')


class loginSerializers(serializers.Serializer):
    phone = serializers.CharField(label='手机号', validators=[phone_validator, ])
    code = serializers.CharField(label="验证码")

    def validate_code(self, value):
        if len(value) != 4:
            # 报错
            raise ValidationError("验证码长度出错")
        if not value.isdecimal():
            # 报错
            raise ValidationError("验证码格式出错")
        phone = self.initial_data.get("phone")
        conn = get_redis_connection()
        code = conn.get(phone)
        if not code:
            raise ValidationError('验证码过期')
        if value != code.decode('utf-8'):
            raise ValidationError('验证码错误')

        return value


# Create your views here.
class login(APIView):
    def post(self, request, *args, **kwargs):
        ser = loginSerializers(data=request.data)  # request.data
        if not ser.is_valid():
            return Response({"Status": False, "message": '验证码信息错误'})

        phone = ser.validated_data.get("phone")
        print(phone)
        # get_or_create 没有就创建 有就查询 返回flase 不为空
        user_object, flag = models.UserInfo.objects.get_or_create(phone=phone)
        print(user_object, flag)  # user_object 是当前用户对象,flag如果有返回
        user_object.token = uuid.uuid4()
        user_object.save()
        print(user_object.token)
        # ser.save()
        return Response({"status": True, "data": {"token": user_object.token, 'phone': phone}})


# 写一个校验器


class MessageSerializer(serializers.Serializer):
    phone = serializers.CharField(label='手机号', validators=[phone_validator, ])


class MessageView(APIView):
    def get(self, request, *args, **kwargs):
        ser = MessageSerializer(data=request.query_params)
        if not ser.is_valid():
            return Response({'status': False, 'message': '手机格式错误'})
        phone = ser.validated_data.get('phone')
        # 3.生成随机验证码

        random_code = random.randint(1000, 9999)
        msg.sendMessage(phone, random_code)
        # 持久化存储
        '''
        from django.core.cache import caches
        '''
        conn = get_redis_connection()  # 基于配置进行链接
        conn.set(phone, random_code, ex=90)  # 设置值并设置过期事件
        print(random_code)
        return Response({"status": True, 'message': '发送成功', "code": str(random_code)})


class DXmessageView(APIView):
    def get(self, request, *args, **kwargs):
        from sts.sts import Sts
        from django.conf import settings
        config = {
            # 临时密钥有效时长，单位是秒
            'duration_seconds': 1800,
            # 固定密钥 id
            'secret_id': settings.TENT['SECRET_ID'],
            # 固定密钥 key
            'secret_key': settings.TENT['SECRET_KEY'],
            # 设置网络代理
            # 'proxy': {
            #     'http': 'xx',
            #     'https': 'xx'
            # },
            # 换成你的 bucket
            'bucket': 'lzw-1301082773',
            # 换成 bucket 所在地区
            'region': 'ap-chengdu',
            # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
            # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
            'allow_prefix': '*',
            # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
            'allow_actions': [
                'name/cos:PostObject',
            ],

        }

        sts = Sts(config)
        response = sts.get_credential()
        return Response(response)


from rest_framework.request import Request


# 发布
class MyAuthentication:
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        # 1.如果用户没有提供token,返回None（我不处理，交给下一个认证类处理，则默认是None）
        if not token:
            return None
        # 2.token错误，,返回None（我不处理，交给下一个认证类处理，则默认是None）
        user_object = models.UserInfo.objects.filter(token=token).first()
        if not user_object:
            return (None, None)

        # 3.认证成功
        return (user_object, token)  # request.user/request.auth


class model_create(APIView):
    authentication_classes = [MyAuthentication, ]

    def post(self, request, *args, **kwargs):
        print(request.data)
        phone = request.data.pop("phone")
        print(request.data)
        imagelist = request.data.pop('image')
        author = models.UserInfo.objects.filter(phone=phone).first()
        detial = models.ArticleDetail.objects.create(content=request.data.get('detial'))
        article_1 = models.Article.objects.create(
            summary=request.data.get('detial')[:10],
            detial=detial,
            author=author,
            location=request.data.get('location') if request.data.get('location') else None,
            date=str(datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
        )
        for i in imagelist:
            models.Picture.objects.create(image_path=i, atricle_image=article_1)
        if request.data.get("title"):
            title = models.Huati.objects.filter(pk=request.data.get("title")).first()
            print(author, title)
            models.Article.objects.create(
                title=title,
            )
            print(article_1.__dict__)

        return Response('成功')


################################### 文章获取#########################
# filter_backends = [MinFilterBackend, MaxFilterBackend]
from rest_framework.filters import BaseFilterBackend


class MinFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        min_id = request.query_params.get('min_id')
        print("min",min_id)
        if min_id:
            return queryset.filter(id__lt=min_id).order_by('-id')
        return queryset


class MaxFilterBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        max_id = request.query_params.get('max_id')
        if max_id:
            return queryset.filter(id__gt=max_id).order_by('id')
        return queryset


class Article(ListAPIView):
    queryset = models.Article.objects.all().order_by("-id")
    serializer_class = MySerializer.AtricleServilizer
    filter_backends = [MaxFilterBackend, MinFilterBackend]
    pagination_class = OldBoyLimitPagination


################################文章详细####################
class NewFiltrBackend(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        article_id = request.query_params.get("id")
        if not article_id:
            return queryset.none()
        return queryset.filter(detial_id=article_id)


class Article_detial(ListAPIView):
    filter_backends = [NewFiltrBackend, ]
    # 根据源码指定queryset类
    queryset = models.Article.objects.all()

    serializer_class = MySerializer.AtricleDetailServilizer


########################################################
#######################话题
# 获取话题信息
class Huati(ListAPIView):
    queryset = models.Huati.objects.all()
    serializer_class = MySerializer.TitleServilizer


# 课上代码图片s

class NewView(CreateAPIView):
    serializer_class = MySerializer.CreateNewsViewModelSerializer

    def perform_create(self, serializer):
        new_object = serializer.save(author_id=1)


# 浏览页面的获取

class Visterfilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        article_id = request.query_params.get("article_id")
        return queryset.filter(article_detail=article_id)


class VisterView(ListAPIView):
    queryset = models.Vister_msg.objects.all()
    filter_backends = [Visterfilter, ]
    serializer_class = MySerializer.Viewserializer


####3################评论#########################
class Article_comment(CreateAPIView):
    serializer_class = MySerializer.ViewComment

    def perform_create(self, serializer):
        serializer.save()
