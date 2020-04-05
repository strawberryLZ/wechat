# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-02-10 10:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('api', '0003_auto_20200210_1127'),
    ]

    operations = [
        migrations.CreateModel(
            name='AuctionPayment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('auction_price', models.IntegerField(verbose_name='每次拍卖的价格')),
                ('auction_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.UserInfo', verbose_name='出价人')),
            ],
            options={
                'verbose_name_plural': '拍卖记录',
            },
        ),
        migrations.CreateModel(
            name='CommodityHome',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveIntegerField(choices=[(1, '未开拍'), (2, '预展中'), (3, '拍卖中'), (4, '已结束')], default=1, verbose_name='标题类型')),
                ('title', models.CharField(max_length=128, verbose_name='标题')),
                ('showtime', models.DateTimeField(verbose_name='预展开始时间')),
                ('endtime', models.DateTimeField(verbose_name='预展结束时间')),
                ('opentime', models.DateTimeField(verbose_name='拍卖开始时间')),
                ('closetime', models.DateTimeField(verbose_name='拍卖结束时间')),
                ('home_price', models.IntegerField(verbose_name='全场保证金额')),
                ('cover', models.CharField(max_length=256, verbose_name='封面')),
                ('read_count', models.IntegerField(default=10, verbose_name='围观次数')),
                ('comm_count', models.IntegerField(default=0, verbose_name='拍卖数量')),
                ('deal_count', models.IntegerField(default=0, verbose_name='出价数')),
            ],
            options={
                'verbose_name_plural': '竞拍首页',
            },
        ),
        migrations.CreateModel(
            name='DetailCommodityPic',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=256, verbose_name='文件名')),
                ('image_path', models.CharField(max_length=256, verbose_name='网络图片地址')),
                ('status', models.PositiveIntegerField(choices=[(1, '轮播'), (2, '详情'), (3, '封面')], default=1, verbose_name='图片类型')),
            ],
            options={
                'verbose_name_plural': '拍品图片',
            },
        ),
        migrations.CreateModel(
            name='Focus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'verbose_name_plural': '关注记录',
            },
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveIntegerField(choices=[(1, '单品保证金'), (2, '全场保证金')], default=1, verbose_name='保证金类型')),
                ('auction_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.UserInfo', verbose_name='保证人')),
                ('home_payment', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auction.CommodityHome', verbose_name='关联全场')),
            ],
            options={
                'verbose_name_plural': '保证记录',
            },
        ),
        migrations.CreateModel(
            name='ShowCommodity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveIntegerField(choices=[(1, '未拍卖'), (2, '拍卖中'), (3, '已结束')], default=1, verbose_name='拍品状态')),
                ('title', models.CharField(max_length=32, verbose_name='标题')),
                ('read_count', models.IntegerField(default=10, verbose_name='围观次数')),
                ('max_price', models.IntegerField(verbose_name='最大价格')),
                ('min_price', models.IntegerField(verbose_name='最小价格')),
                ('deal_price', models.IntegerField(verbose_name='起拍价格')),
                ('add_price', models.IntegerField(default=100, verbose_name='加价')),
                ('payment_price', models.IntegerField(verbose_name='单品保证金额')),
                ('auction_count', models.IntegerField(default=0, verbose_name='出价次数')),
                ('home', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.CommodityHome', verbose_name='专场')),
            ],
            options={
                'verbose_name_plural': '拍品内容',
            },
        ),
        migrations.AddField(
            model_name='payment',
            name='show_Payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auction.ShowCommodity', verbose_name='关联单品'),
        ),
        migrations.AddField(
            model_name='focus',
            name='show_comm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.ShowCommodity', verbose_name='拍品'),
        ),
        migrations.AddField(
            model_name='focus',
            name='user_comm',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.UserInfo', verbose_name='用户'),
        ),
        migrations.AddField(
            model_name='detailcommoditypic',
            name='show_image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.ShowCommodity', verbose_name='关联拍品'),
        ),
        migrations.AddField(
            model_name='auctionpayment',
            name='show_Auction',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.ShowCommodity', verbose_name='关联拍品'),
        ),
    ]
