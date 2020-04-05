from rest_framework.generics import ListAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework import serializers
from api import models
from django.forms import model_to_dict  # 对象转字典


class AtricleServilizer(serializers.ModelSerializer):
    image_list = serializers.SerializerMethodField()
    author_name = serializers.CharField(source="author.nickName", read_only=True)
    author_url = serializers.CharField(source="author.avatarUrl", read_only=True)
    author_location = serializers.CharField(source="author.location", read_only=True)

    # max_1=
    # min_1=
    # cover = serializers.SerializerMethodField()

    def get_image_list(self, obj):
        print('xxxx', obj.picture_set.all())
        return obj.picture_set.all().first().image_path

    class Meta:
        model = models.Article
        fields = ["id", "title", "summary", "author", "location", "detial", "image_list", "author_name", "author_url",
                  "goods",
                  "author_location", ]


class TitleServilizer(serializers.ModelSerializer):
    class Meta:
        model = models.Huati
        fields = "__all__"


class AtricleDetailServilizer(serializers.ModelSerializer):
    image_list = serializers.SerializerMethodField()
    author = serializers.SerializerMethodField()
    article_content = serializers.CharField(source="content", read_only=True)
    title = serializers.CharField(source="title.title", read_only=True)
    date = serializers.SerializerMethodField()
    viewer = serializers.SerializerMethodField()
    topic = serializers.SerializerMethodField()
    comment = serializers.SerializerMethodField()

    """
    取出对应的话题
    """

    def get_author(self, obj):
        return model_to_dict(obj.author, ["nickName", "avatarUrl"])

    def get_topic(self, obj):
        if not obj.title:
            return
        return model_to_dict(obj.title, ['id', 'title'])

    """
    取出浏览次数
    """

    def get_viewer(self, obj):
        # 手写的而已
        queryset = models.Vister_msg.objects.filter(article_detail=obj.id)
        viewer_object_list = queryset.order_by("-id")[0:10]
        # 结果值
        context = {
            'count': queryset.count(),
            'result': [model_to_dict(i.author, ['nickName', 'avatarUrl']) for i in viewer_object_list]
        }
        return context

    """
    时间格式化也可以使用
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    """

    def get_date(self, obj):
        return obj.date.strftime('%Y-%m-%d')

    def get_image_list(self, obj):
        return [i.image_path for i in obj.picture_set.all()]

    def get_comment(self, obj):
        """
        获取所有一级评论
        :param obj:
        :return:
        """
        first_queryset = models.Comment.objects.filter(article=obj, depth=1).order_by("-id")[0:10].values(
            "id",
            'content',
            'depth',
            'user__nickName',
            'user__avatarUrl',
            'date',
        )
        # 一级评论id的列表
        first_id_list = [i['id'] for i in first_queryset]
        from django.db.models import Max
        """
        取出一级评论下的最新的一条二级评论
        """
        result = models.Comment.objects.filter(article=obj, depth=2, reply_id__in=first_id_list) \
            .values("reply_id").annotate(max_id=Max('id'))
        # 分组取出最新的一条
        print(result)
        second_id_list = [item["max_id"] for item in result]

        second_queryset = models.Comment.objects.filter(id__in=second_id_list).values(
            "id",
            'content',
            'depth',
            'user__nickName',
            'user__avatarUrl',
            'date',
            'reply_id',
            "reply__user__nickName"
        )
        import collections
        first_dict = collections.OrderedDict()
        for item in first_queryset:
            item['date'] = item['date'].strftime('%Y-%m-%d')
            first_dict[item['id']] = item
        for node in second_queryset:
            # child回复2级评论就是三级评论
            print(node["reply_id"])
            first_dict[node['reply_id']]['child'] = [node, ]
        print("一个有序字典", first_dict)
        return first_dict.values()

    class Meta:
        model = models.Article
        fields = ["id", "title", "summary", "author", "location", "detial", "image_list",
                  "date", "topic", "comment", "article_content", "goods", "comment", "viewer"]


# 课上发布
class CreateDetailViewModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ArticleDetail
        fields = "__all__"


class CreateTopicViewModelSerializer(serializers.Serializer):
    image_path = serializers.CharField()


class CreateNewsViewModelSerializer(serializers.ModelSerializer):
    # 序列化器嵌套 使用many=True 可以传递多个
    detial = CreateDetailViewModelSerializer()
    imageList = CreateTopicViewModelSerializer(many=True)

    class Meta:
        model = models.Article
        exclude = ["goods", "date", "comment_count"]

    def create(self, validated_data):
        # 把获取到的image窃走
        detial = validated_data.get("detial")
        detial = models.ArticleDetail.objects.create(**detial)
        validated_data["detial"] = detial
        image_List = validated_data.pop("imageList")

        # 文章表的数据表数据
        news_object = models.Article.objects.create(**validated_data)
        # 图片表数据的数据
        data_list = models.Picture.objects.bulk_create(
            [models.Picture(**info, atricle_image=news_object) for info in image_List]
        )

        news_object.imageList = data_list

        return news_object


# 评论者
class Viewserializer(serializers.ModelSerializer):
    author = serializers.SerializerMethodField()

    class Meta:
        model = models.Vister_msg
        fields = "__all__"

    def get_author(self, obj):  # 当前model类对象
        return model_to_dict(obj.author, fields=["id", "nickName", "avatarUrl"])


# 创建评论
class  ViewComment(serializers.ModelSerializer):
    class Meta:
        model = models.Comment
        exclude=["article","user"]

    # self 当前序列化器对象
    def create(self, validated_data):
        if self.context["request"].data.get("cid"):
            cid=self.context["request"].data.get("cid")
            validated_data["reply_id"] = cid
        root_id=self.context["request"].data.get("rid")
        validated_data["root_id"] = root_id
        article_id=self.context["request"].data.get("nid")
        print("post", validated_data)
        # article_id = validated_data.pop("nid")
        validated_data["article_id"] = article_id
        user_object = self.context['request'].user
        validated_data["user"] = user_object
        comment_object = models.Comment.objects.create(**validated_data)
        return comment_object
