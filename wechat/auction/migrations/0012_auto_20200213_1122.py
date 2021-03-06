# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2020-02-13 03:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0003_auto_20200210_1127'),
        ('auction', '0011_auto_20200212_1848'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=32, verbose_name='收货人姓名')),
                ('phone', models.CharField(max_length=11, verbose_name='联系电话')),
                ('city', models.CharField(max_length=64, verbose_name='收货地址')),
                ('detail', models.CharField(max_length=64, verbose_name='详细地址')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.UserInfo', verbose_name='用户')),
            ],
        ),
        migrations.CreateModel(
            name='DepositRefundRecord',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(max_length=64, verbose_name='流水号')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, '退款中'), (2, '退款成功')], verbose_name='状态')),
                ('amount', models.PositiveIntegerField(verbose_name='退款金额')),
            ],
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status', models.PositiveSmallIntegerField(choices=[(1, '未支付'), (2, '代收获'), (3, '未支付'), (4, '未支付')], verbose_name='状态')),
                ('uid', models.CharField(max_length=64, verbose_name='流水号')),
                ('price', models.PositiveIntegerField(verbose_name='出价')),
                ('real_price', models.PositiveIntegerField(null=True, verbose_name='实际支付金额')),
                ('deposit_price', models.PositiveIntegerField(verbose_name='使用保证金金额')),
                ('create_date', models.DateTimeField(auto_now_add=True, verbose_name='创建时间')),
                ('address', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auction.Address', verbose_name='收货地址')),
            ],
        ),
        migrations.AlterModelOptions(
            name='payment',
            options={},
        ),
        migrations.AddField(
            model_name='payment',
            name='amount',
            field=models.PositiveIntegerField(default=1, verbose_name='金额'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='deposit_type',
            field=models.PositiveIntegerField(choices=[(1, '单品保证金'), (2, '全场保证金')], default=1, verbose_name='保证金类型'),
        ),
        migrations.AddField(
            model_name='payment',
            name='pay_type',
            field=models.SmallIntegerField(choices=[(1, '微信'), (2, '余额')], default=1, verbose_name='支付方式'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='payment',
            name='uid',
            field=models.CharField(default=1, max_length=64, verbose_name='流水号'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='payment',
            name='home_payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auction.CommodityHome', verbose_name='专场'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='show_Payment',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='auction.ShowCommodity', verbose_name='单品'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='status',
            field=models.PositiveSmallIntegerField(choices=[(1, '未支付'), (2, '支付成功')], default=1, verbose_name='状态'),
        ),
        migrations.AddField(
            model_name='order',
            name='deposit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.Payment', verbose_name='保证金'),
        ),
        migrations.AddField(
            model_name='order',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.ShowCommodity', verbose_name='拍品'),
        ),
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.UserInfo', verbose_name='用户'),
        ),
        migrations.AddField(
            model_name='depositrefundrecord',
            name='deposit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auction.Payment', verbose_name='保证金'),
        ),
    ]
