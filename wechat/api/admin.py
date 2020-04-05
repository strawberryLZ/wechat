from django.contrib import admin
from api import models
admin.site.register(models.UserInfo)
admin.site.register(models.Picture)
admin.site.register(models.Huati)
admin.site.register(models.Article)
admin.site.register(models.ArticleDetail)
admin.site.register(models.Comment)
admin.site.register(models.Collection)
# Register your models here.
