from django.db import models
from api import models as api

# Create your models here.'

"""
拍卖专场
"""


class CommodityHome(models.Model):
    home_status = (
        (1, "未开拍"),
        (2, "预展中"),
        (3, "拍卖中"),
        (4, "已结束"),
    )
    status = models.PositiveIntegerField(choices=home_status, verbose_name='标题类型', default=1)
    title = models.CharField(max_length=127, verbose_name='标题')
    showtime = models.DateTimeField(verbose_name='预展开始时间')
    endtime = models.DateTimeField(verbose_name='预展结束时间')
    opentime = models.DateTimeField(verbose_name='拍卖开始时间')
    closetime = models.DateTimeField(verbose_name='拍卖结束时间')
    home_price = models.IntegerField(verbose_name="全场保证金额")
    cover = models.FileField(verbose_name='封面', max_length=256)
    read_count = models.IntegerField(verbose_name='围观次数', default=10)
    comm_count = models.IntegerField(verbose_name='拍卖数量', default=0)
    deal_count = models.IntegerField(verbose_name='出价数', default=0)
    total_price = models.IntegerField(verbose_name="全场拍卖总金额", null=True, blank=True)

    class Meta:
        verbose_name_plural = "竞拍首页"

    def __str__(self):
        return self.title


"""
拍品内容
"""


class ShowCommodity(models.Model):
    show_status = (
        (1, '未开拍'),
        (2, '预展中'),
        (3, '拍卖中'),
        (4, '成交'),
        (5, '流拍'),
    )
    status = models.PositiveIntegerField(verbose_name='拍品状态', choices=show_status, default=1)
    title = models.CharField(max_length=32, verbose_name='标题')
    read_count = models.IntegerField(verbose_name='围观次数', default=10)
    uid = models.CharField(verbose_name='图录号', max_length=12)

    home = models.ForeignKey(verbose_name='专场', to="CommodityHome")
    cover = models.FileField(verbose_name='封面', max_length=256)
    max_price = models.IntegerField(verbose_name='参考最高价格')
    min_price = models.IntegerField(verbose_name='参考最低价格')
    first_price = models.PositiveIntegerField(verbose_name='起拍价')
    end_price = models.PositiveIntegerField(verbose_name='成交价', null=True, blank=True)
    add_price = models.IntegerField(verbose_name='加价', default=100)
    payment_price = models.IntegerField(verbose_name='单品保证金额')
    auction_count = models.IntegerField(verbose_name='出价次数', default=0)

    class Meta:
        verbose_name_plural = "拍品内容"

    def __str__(self):
        return self.title


"""
拍品规格
"""


class AuctionItemDetail(models.Model):
    """
    拍品详细规格
    """
    item = models.ForeignKey(verbose_name='拍品', to='ShowCommodity')
    key = models.CharField(verbose_name='项', max_length=16)
    value = models.CharField(verbose_name='值', max_length=32)

    class Meta:
        verbose_name_plural = '拍品规格'


"""
拍品图片
"""


class DetailCommodityPic(models.Model):
    carousel = models.BooleanField(verbose_name='是否在轮播中显示', default=False)
    show_image = models.ForeignKey(verbose_name="关联拍品", to="ShowCommodity")
    # key = models.CharField(verbose_name='文件名', max_length=256)
    image_path = models.FileField(verbose_name='网络图片地址', max_length=256)

    class Meta:
        verbose_name_plural = "拍品图片"

    def __str__(self):
        return self.show_image.title


"""
拍卖记录
"""


class AuctionPayment(models.Model):
    status_choices = (
        (1, '竞价'),
        (2, '成交'),
        (3, '逾期未付款'),
    )
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=status_choices, default=1)
    auction_price = models.IntegerField(verbose_name="出价")
    auction_item = models.ForeignKey(verbose_name='关联拍品', to="ShowCommodity")
    auction_user = models.ForeignKey(verbose_name="出价人", to="api.UserInfo")

    class Meta:
        verbose_name_plural = "拍卖记录"


"""

保证金
保证支付记录
单品保证金
全场保证金
"""


class Payment(models.Model):
    payment_status = (

        (1, "单品保证金"),
        (2, "全场保证金"),

    )
    status_choices = (
        (1, '未支付'),
        (2, '支付成功')
    )
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=status_choices, default=1)
    uid = models.CharField(verbose_name='流水号', max_length=64)
    deposit_type = models.PositiveIntegerField(verbose_name='保证金类型', choices=payment_status, default=1)
    show_Payment = models.ForeignKey(verbose_name='单品', to="ShowCommodity", null=True, blank=True)
    auction_user = models.ForeignKey(verbose_name="保证人", to="api.UserInfo")
    home_payment = models.ForeignKey(verbose_name='专场', to="CommodityHome", null=True, blank=True)
    pay_type_choices = (
        (1, '微信'),
        (2, '余额')
    )
    pay_type = models.SmallIntegerField(verbose_name='支付方式', choices=pay_type_choices)

    amount = models.PositiveIntegerField(verbose_name='缴纳金额')
    balance = models.PositiveIntegerField(verbose_name='可用金额')

    class Meta:
        verbose_name_plural = "保证记录"

    def __str__(self):
        if self.show_Payment:
            return "%s++单品+%s" % (self.auction_user.phone, self.show_Payment.title)
        else:
            return "%s++全场+%s" % (self.auction_user.phone, self.home_payment.title)


class DepositRefundRecord(models.Model):
    """ 保证金退款记录 """

    uid = models.CharField(verbose_name='流水号', max_length=64)
    status_choices = (
        (1, "退款中"),
        (2, '退款成功')
    )
    status = models.PositiveSmallIntegerField(verbose_name='状态', choices=status_choices)
    deposit = models.ForeignKey(verbose_name='保证金', to='Payment')
    amount = models.PositiveIntegerField(verbose_name='退款金额')


class DepositDeduct(models.Model):
    """ 扣除保证金 """
    order = models.ForeignKey(verbose_name='订单', to='Order')
    amount = models.PositiveIntegerField(verbose_name='金额')

    deduct_type_choices = (
        (1, '逾期扣款'),
        (2, '支付抵扣')
    )
    deduct_type = models.SmallIntegerField(verbose_name='扣款类型', choices=deduct_type_choices, default=1)


"""
关注 有关注记录说明关注了
"""


class Focus(models.Model):
    user_comm = models.ForeignKey(verbose_name='用户', to="api.UserInfo")
    show_comm = models.ForeignKey(verbose_name='拍品', to="ShowCommodity")

    class Meta:
        verbose_name_plural = "关注记录"


class AuctionTask(models.Model):
    """
    任务id
    """
    auction = models.OneToOneField(verbose_name="专场", to='CommodityHome')
    preview_task = models.CharField(verbose_name='Celery预展ID', max_length=64)
    auction_task = models.CharField(verbose_name='Celery拍卖任务ID', max_length=64)
    auction_end_task = models.CharField(verbose_name='Celery拍卖结束ID', max_length=64)


class Order(models.Model):
    """
    订单,拍卖结束时,执行定时任务处理;
        - 拍到商品,创建订单
        - 没拍到商品,则退款到原账户
    订单支付 支付的金额 扣除可用保证金 添加抵扣保证金
    """
    ##订单状态
    status_choices = (
        (1, '未支付'),
        (2, '待收货'),
        (3, '已完成'),
        (4, '逾期未支付'),
    )
    status = models.PositiveSmallIntegerField(verbose_name="状态", choices=status_choices, default=1)
    pay_choices = (
        (1, '微信'),
        (2, '余额'),
    )
    pay_type = models.PositiveSmallIntegerField(verbose_name="支付状态", choices=status_choices, default=2)

    uid = models.CharField(verbose_name="流水号", max_length=64)
    user = models.ForeignKey(verbose_name="用户", to=api.UserInfo)
    item = models.ForeignKey(verbose_name="拍品", to=ShowCommodity)
    deposit = models.ForeignKey(verbose_name="保证金", to=Payment)
    price = models.PositiveIntegerField(verbose_name='出价')
    real_price = models.PositiveIntegerField(verbose_name='实际支付金额', null=True, blank=True)
    deposit_price = models.PositiveIntegerField(verbose_name='使用保证金金额', null=True, blank=True)
    address = models.ForeignKey(verbose_name='收货地址', to='Address', null=True, blank=True)

    create_date = models.DateTimeField(verbose_name='创建时间', auto_now_add=True)


class Address(models.Model):
    """ 地址 """
    name = models.CharField(verbose_name='收货人姓名', max_length=32)
    phone = models.CharField(verbose_name='联系电话', max_length=11)
    # city = models.CharField(verbose_name='收货地址', max_length=64)
    detail = models.CharField(verbose_name='详细地址', max_length=64)
    user = models.ForeignKey(verbose_name='用户', to=api.UserInfo)


class Discounts(models.Model):
    status_choices = (
        (1, "未发放"),
        (2, "可领取"),
        (3, "已结束"),
    )
    status = models.PositiveSmallIntegerField(verbose_name="状态", choices=status_choices, default=2)
    name = models.CharField(verbose_name='优惠卷名称', max_length=32)
    auction = models.ForeignKey(verbose_name="专场", to=CommodityHome)
    start = models.DateTimeField(verbose_name='领取开始时间', null=True, blank=True)
    end = models.DateTimeField(verbose_name='领取结束时间', null=True, blank=True)
    price = models.IntegerField(verbose_name="抵扣金额")
    cover = models.FileField(verbose_name='封面', max_length=256)
    total_count = models.IntegerField(verbose_name="初始数量")
    use_count = models.IntegerField(verbose_name="领取数量", default=0)
    apply_start_task_id = models.CharField(verbose_name='celery开始ID', max_length=64, null=True, blank=True)
    apply_stop_task_id = models.CharField(verbose_name='celery结束ID', max_length=64, null=True, blank=True)
    deleted = models.BooleanField(verbose_name="是否删除", default=False)


class Userdicount(models.Model):
    user = models.ForeignKey(verbose_name="用户", to=api.UserInfo)
    dis = models.ForeignKey(verbose_name="优惠卷", to=Discounts)
    status_choices = (
        (1, "未使用"),
        (2, "已使用"),
        (3, "已过期"),
    )
    status = models.PositiveSmallIntegerField(verbose_name="状态", choices=status_choices, default=1)
    ord = models.ForeignKey(verbose_name="订单", to=Order, null=True, blank=True)
