from django.db import models

rpg_list = [
    (1, "普通用户"),
    (2, "管理员"),
    (3, "普通用户"),
]


class UserInfo(models.Model):
    nickName = models.CharField(verbose_name='名称', max_length=256)
    phone = models.CharField(verbose_name='手机号', max_length=11, unique=True)
    avatarUrl = models.CharField(verbose_name='图片路径', max_length=256)
    token = models.CharField(verbose_name='用户TOKEN', max_length=64, null=True, blank=True)
    rpg = models.CharField(choices=rpg_list, verbose_name='用户身份', max_length=64, null=True, blank=True, default=0)
    location = models.CharField(verbose_name='地理位置', max_length=64, null=True, blank=True)
    balance=models.IntegerField(verbose_name="余额",default=0)
    class Meta:
        verbose_name = '用户'
        # 定义复数时的名称（去除复数的s）
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.phone


class Picture(models.Model):
    atricle_image = models.ForeignKey(verbose_name='图片外键', max_length=32, to="Article")
    image_path = models.CharField(verbose_name='文章图片路径', max_length=256, null=True, blank=True)


class Huati(models.Model):
    title = models.CharField(verbose_name='标题', max_length=32)
    count = models.IntegerField(verbose_name='人数',default=0)

    class Meta:
        # 定义在管理后台显示的名称
        verbose_name = '话题'
        # 定义复数时的名称（去除复数的s）
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.title


class Article(models.Model):
    """ 文章表 """
    title = models.ForeignKey(verbose_name='标题', max_length=31, to="Huati", null=True, blank=True)
    summary = models.CharField(verbose_name='简介', max_length=255,)
    comment_count = models.IntegerField(verbose_name='评论数', default=0)
    goods = models.IntegerField(verbose_name='点赞数', default=0)
    author = models.ForeignKey(verbose_name='用户', to='UserInfo', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)
    location = models.CharField(verbose_name='地理位置', max_length=64, null=True, blank=True)
    detial = models.OneToOneField(verbose_name='文章表', to='ArticleDetail', null=True, blank=True)

    class Meta:
        # 定义在管理后台显示的名称
        verbose_name = '文章'
        # 定义复数时的名称（去除复数的s）
        verbose_name_plural = verbose_name

    def __str__(self):
        return str(self.id)


class ArticleDetail(models.Model):
    content = models.TextField(verbose_name='内容')
    Coll_count = models.IntegerField(verbose_name='收藏数', default=0)

    class Meta:
        verbose_name = '文章详细'
        # 定义复数时的名称（去除复数的s）
        verbose_name_plural = verbose_name


class Comment(models.Model):
    """ 评论表 """
    article = models.ForeignKey(verbose_name='文章', to='Article')
    content = models.TextField(verbose_name='评论内容')
    date = models.DateTimeField(verbose_name='评论时间', auto_now_add=True)
    user = models.ForeignKey(verbose_name='评论者', to='UserInfo')
    reply=models.ForeignKey(verbose_name='回复的评论',null=True, blank=True,to="self",related_name='replys')
    # 评论层级
    depth = models.IntegerField(verbose_name='评论深度', default=0, blank=True)
    root=models.ForeignKey(verbose_name='根评论',to="self",null=True, blank=True,related_name='roots')
    favor_count = models.PositiveIntegerField(verbose_name='赞数', default=0)
    class Meta:
        # 定义表名
        db_table = "Comment"
        # 定义在管理后台显示的名称
        verbose_name = '评论内容'
        # 定义复数时的名称（去除复数的s）
        verbose_name_plural = verbose_name

    def __str__(self):
        return "%s+++%s" % (self.user, self.article)


class Collection(models.Model):
    collection_book = models.ForeignKey(verbose_name="文章收藏", to='Article')


class Vister_msg(models.Model):
    author = models.ForeignKey(verbose_name="关联用户", to="UserInfo")
    vister_count = models.IntegerField(verbose_name="浏览数", default=0)
    article_detail = models.ForeignKey(verbose_name="文章详细", max_length=32, to="ArticleDetail")

class goods(models.Model):
    pass

class Coupons(models.Model):
    pass