#!/usr/bin/env python # -*- coding:utf-8 -*
import uuid
import itertools
from celery import shared_task
from auction import models
import datetime

'''
预展中
'''


@shared_task
def to_preview_status_task(auction_id):
    models.CommodityHome.objects.filter(id=auction_id).update(status=2)
    models.ShowCommodity.objects.filter(home_id=auction_id).update(status=2)


"""
预展结束开始拍卖
"""


@shared_task
def to_auction_status_task(auction_id):
    models.CommodityHome.objects.filter(id=auction_id).update(status=3)
    models.ShowCommodity.objects.filter(home_id=auction_id).update(status=3)


"""
拍卖结束更新状态
值的设置
    先设置存储拍得商品的id set集合
1.筛选
2.筛选专场和单品对象
3.循环单品 
    3.1有出价的单品筛选出最高价格 并更改为成交状态 设置成交价格保存 
    3.2没有出价的单品的状态就是流拍
4.计算出专场的成交价(所有单品成交价的总和)
5.保证金
    5.1获取最高价格的人(拍品拍得的人)的保证金类型
        5.1.1筛选是否单品保证金
            单品保证金 保证金关联专场的值为null
        5.1.2否则是全场保证金
            全场保证金 保证金关联单品的值为null
    5.2把所有拍得商品缴纳保证金 进行汇总
6.生成订单
7.调用定时任务如果24小时之内没有缴纳就扣除保证金 和正常退还保证金
    更新专场的总成交额
8.缴纳保证金但是没有拍得商品
    要剔除exclude拍得的人
    8.1 专场保证金
    8.2 全场保证金    
9.24小时之后进行退还保证金和扣除保证金（执行celery任务）
    9.1 更改订单状态 为逾期未支付
    9.2 更改拍品状态 为逾期未支付
    9.3 直接扣除单品保证金
    9.4 进行全场保证金的扣除
        9.4.1如果单品保证金大于缴纳的全场保证金 就之际进行扣除并结束操作
        9.4.2有剩余并且有其他订单 就不进行退款操作等待所有订单结束 结束擦欧总
        9.4.3有剩余并且没有订单 进行退款      
    9.5退款是退到余额还是微信
        退款成功要清空缴纳保证金的余额
"""


@shared_task
def end_auction_task(auction_id):
    """
    拍卖结束要做的事情
    :param auction_id:对应的专场id
    :return:
    """
    models.CommodityHome.objects.filter(id=auction_id).update(status=4)
    models.ShowCommodity.objects.filter(home_id=auction_id).update(status=4)

    luck_auction_deposit_id = set()  # 拍得商品的人 进行去重防止全场保证金处理重复
    total_unfortunate_list = []  # 没有拍得商品的单品保证金人选
    total = 0  # 总价格
    auction_object = models.CommodityHome.objects.filter(id=auction_id).first()

    # 拍品列表
    item_object_list = models.ShowCommodity.objects.filter(home_id=auction_id)
    for item_object in item_object_list:
        luck_object = models.AuctionPayment.objects.filter(auction_item=item_object).order_by("-auction_price").first()
        if not luck_object:
            item_object.status = 5
            item_object.save()
            continue
        luck_object.status = 2
        luck_object.save()

        # 拍品:设置成交价
        item_object.deal_price = luck_object.auction_price
        item_object.save()
        # 总成交价格
        total += luck_object.auction_price
        # 获取当前用户的保证金专场对象
        # 全场保证金

        deposit_object = models.Payment.objects.filter(
            auction_user=luck_object.auction_user,
            show_Payment=item_object,
            deposit_type=1).first()
        # 单品保证金
        print("全场",deposit_object)
        if not deposit_object:
            print("单品")
            deposit_object = models.Payment.objects.filter(
                auction_user=luck_object.auction_user,
                home_payment=auction_object,
                deposit_type=2,
                show_Payment__isnull=True).first()
        # 所有拍到商品的人缴纳的保证金id
        print("保证金id值",deposit_object.id)
        luck_auction_deposit_id.add(deposit_object.id)

        # 生成订单为(待支付)
        order_object = models.Order.objects.create(
            uid=uuid.uuid4(),
            status=1,
            user=luck_object.auction_user,
            deposit=deposit_object,
            item=item_object,
            price=luck_object.auction_price,
        )
        # 单品保证金 所有没有拍到商品并且缴纳的是单品保证金记录
        item_unfortunate_list = models.Payment.objects.filter(show_Payment=item_object, deposit_type=1).exclude(
            auction_user=luck_object.auction_user)
        total_unfortunate_list.extend(item_unfortunate_list)
        print("单品保证金列表的值",total_unfortunate_list)
        date = datetime.datetime.utcnow() + datetime.timedelta(minutes=1)
        print("走这了没")
        task_id = twenty_four_hour.apply_async(args=[order_object.id], eta=date).id
        print(task_id)
        order_object.twenty_four_task_id = task_id
        order_object.save()
    #专场显示的总拍卖金额
    auction_object.total_price = total
    auction_object.save()

    auction_unfortunate_list = models.Payment.objects.filter(
        deposit_type=2,
        home_payment=auction_object,
        show_Payment__isnull=True).exclude(id__in=luck_auction_deposit_id)
    #微信退款
    for deposit in itertools.chain(total_unfortunate_list, auction_unfortunate_list):
        uid = uuid.uuid4()
        if deposit.pay_type == 1:
            # res = refund(uid, deposit.uid, deposit.amount, deposit.amount)
            res = True
            models.DepositRefundRecord.objects.create(uid=uid, status=2 if res else 1, amount=deposit.amount,
                                                      deposit=deposit)
            if res:
                deposit.balance = 0
                deposit.save()
        else:
            "保证金记录对应的用户余额加入用户余额中"
            deposit.auction_user.balance += deposit.amount
            deposit.auction_user.save()
            models.DepositRefundRecord.objects.create(uid=uid, status=2, amount=deposit.amount, deposit=deposit)
            deposit.balance = 0
            deposit.save()


@shared_task
def twenty_four_hour(order_id):
    """24小时"""
    print("24小时")
    order_object = models.Order.objects.filter(id=order_id).first()
    if order_object.status != 1:
        return
    order_object.status = 4
    order_object.save()
    order_object.item.status = 6
    order_object.item.save()
    if order_object.deposit.deposit_type == 1:
        order_object.deposit.balance = 0
        order_object.deposit.save()
        models.DepositDeduct.objects.create(order=order_object, amount=order_object.deposit.amount)
        return

    if order_object.deposit.balance <= order_object.item.deposit:
        order_object.deposit.balance = 0
        order_object.deposit.save()
        models.DepositDeduct.objects.create(order=order_object, amount=order_object.deposit.balance)
        return
    order_object.deposit.balance -= order_object.item.deposit
    order_object.deposit.save()
    models.DepositDeduct.objects.create(order=order_object, amount=order_object.item.deposit)
    exists = models.Order.objects.filter(
        user=order_object.user,
        status=1,
        item__auction_id=order_object.deposit.auction).exclude(id=order_id).exists()
    if exists:
        return
    uid = uuid.uuid4()
    if order_object.deposit.pay_type == 1:
        # res = refund(uid, deposit.uid, deposit.amount, deposit.amount)
        res = True
        models.DepositRefundRecord.objects.create(
            uid=uid,
            status=2 if res else 1,
            amount=order_object.deposit.balance,
            deposit=order_object.deposit)
        if res:
            order_object.deposit.balance = 0
            order_object.deposit.save()
        else:
            order_object.deposit.user.balance += order_object.deposit.balance
            order_object.deposit.user.save()
            models.DepositRefundRecord.objects.create(
                uid=uid,
                status=2,
                amount=order_object.deposit.balance,
                deposit=order_object.deposit
            )
            order_object.deposit.balance = 0
            order_object.deposit.save()

############优惠卷的定时任务的使用####################
"""
优惠卷使用开始时间
"""
@shared_task
def apply_start_discount(discount_id):
    """
    :param discount_id:传入优惠卷id进行数据的更新
    :return: 不用写返回值
    """
    models.Discounts.objects.filter(pk=discount_id).update(status=2)

"""
优惠卷到期
"""
@shared_task
def apply_stop_discount(discount_id):
    """
    :param discount_id:传入优惠卷id进行数据的更新
    :return: 不用写返回值
    """
    models.Discounts.objects.filter(pk=discount_id).update(status=3)