from django import forms
from auction import models
import uuid
from django.forms import widgets
from django.db.models.fields.files import FieldFile
from django.core.files.uploadedfile import InMemoryUploadedFile
from utils.upload1 import upload

# !/usr/bin/env python
# -*- coding:utf-8 -*-
from django.forms import ModelForm


class BootStrapModelForm(ModelForm):
    exclude_bootstrap_class = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for name, field in self.fields.items():
            if name in self.exclude_bootstrap_class:
                continue
            old_class = field.widget.attrs.get('class', "")
            field.widget.attrs['class'] = old_class + ' form-control'


class HomeModelForm(forms.ModelForm):
    class Meta:
        # 指定model类
        model = models.CommodityHome
        # 对应显示的字段
        fields = "__all__"
        # 指定label值
        widgets = {  # 插件
            # 'endtime': forms.TextInput(attrs={'type': 'date'}),
            # 'showtime': forms.TextInput(attrs={'type': 'date'}),
            # 'opentime': forms.TextInput(attrs={'type': 'date'}),
            # 'closetime': forms.TextInput(attrs={'type': 'date'}),
            # 'cover': forms.TextInput(attrs={'type': 'file'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name == "cover":
                continue
            from multiselectfield.forms.fields import MultiSelectFormField
            if not isinstance(field, MultiSelectFormField):
                field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = self.cleaned_data
        # 上传文件
        cover_file_object = cleaned_data.get("cover")
        if not cover_file_object or isinstance(cover_file_object, FieldFile):
            return cleaned_data

        key = cover_file_object.name.rsplit('.', maxsplit=1)[-1]
        file_name = "{0}.{1}".format(str(uuid.uuid4()), key)
        cleaned_data['cover'] = upload(cover_file_object, file_name)
        return cleaned_data


class Item_Add_Editor(forms.ModelForm):
    class Meta:
        model = models.ShowCommodity
        fields = "__all__"
        # 默认使用传参 使用init 继承父类的init方法因为要保留父类的方法

    def __init__(self, *args, **kwargs):
        # self就是当前类对象 默认self别的值也可以
        super().__init__(*args, **kwargs)
        # 进行批量样式的更改
        # for循环解构

        """
        或者进行判断
        class AuctionModelForm(BootStrapModelForm):
            exclude_bootstrap_class = ['cover']

            class Meta:
                model = models.Auction
                exclude = ['status', 'total_price', 'goods_count', 'bid_count', 'look_count', 'video']

            def clean(self):#全局钩子
                cleaned_data = self.cleaned_data
                # 上传文件
                cover_file_object = cleaned_data.get('cover')
                if not cover_file_object or isinstance(cover_file_object, FieldFile):
                    return cleaned_data
        
                ext = cover_file_object.name.rsplit('.', maxsplit=1)[-1]
                file_name = "{0}.{1}".format(str(uuid.uuid4()), ext)
                cleaned_data['cover'] = upload_file(cover_file_object, file_name)
                return cleaned_data
        """
        for field_name, field_obj in self.fields.items():
            if field_name == "cover":
                continue
            # 保留原来的样式
            # 每个对象都有对应插件
            old_class = field_obj.widget.attrs.get('class', "")
            field_obj.widget.attrs['class'] = old_class + ' form-control'

    def clean_cover(self):
        # cleaned_data = self.cleaned_data
        file_obj = self.cleaned_data.get("cover")
        if not file_obj or isinstance(file_obj, FieldFile):
            return file_obj
        key = file_obj.name.rsplit(".")[-1]
        file_name = "{0}.{1}".format(str(uuid.uuid4()), key)
        file_obj = upload(file_obj, file_name)
        return file_obj


class AuctionDetailModelForm(ModelForm):
    class Meta:
        model = models.AuctionItemDetail
        exclude = ['item']


class AuctionItemImageModelForm(BootStrapModelForm):
    class Meta:
        model = models.DetailCommodityPic
        exclude = ['show_image', 'order']

    def clean_carousel(self):
        value = self.cleaned_data.get('carousel')
        return bool(value)

    def clean(self):
        cleaned_data = self.cleaned_data
        print("全局", cleaned_data)
        # 上传文件
        cover_file_object = cleaned_data.get('image_path')
        if not cover_file_object or isinstance(cover_file_object, FieldFile):
            return cleaned_data

        ext = cover_file_object.name.rsplit('.', maxsplit=1)[-1]
        file_name = "{0}.{1}".format(str(uuid.uuid4()), ext)
        cleaned_data['image_path'] = upload(cover_file_object, file_name)
        return cleaned_data


class DiscountModelForm(BootStrapModelForm):
    exclude_bootstrap_class = ["cover"]

    class Meta:
        model = models.Discounts
        exclude = ["use_count"]

    def clean_cover(self):
        cover_object = self.cleaned_data.get("cover")
        if not cover_object or isinstance(cover_object, FieldFile):
            return cover_object
        ext = cover_object.name.rsplit('.', maxsplit=1)[-1]
        file_name = "{0}.{1}".format(str(uuid.uuid4()), ext)
        cover_object = upload(cover_object, file_name)
        return cover_object
