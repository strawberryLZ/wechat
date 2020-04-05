from rest_framework import serializers
from rest_framework import exceptions
from auction import models
from django.forms import model_to_dict


class SonSerializers(serializers.ModelSerializer):
    cover = serializers.CharField()
    image_list = serializers.SerializerMethodField()
    deposit = serializers.SerializerMethodField()

    class Meta:
        model = models.ShowCommodity
        fields = "__all__"

    def get_image_list(self, obj):
        print([i.image_path.name for i in obj.detailcommoditypic_set.all()])
        return [i.image_path.name for i in obj.detailcommoditypic_set.all()]

    def get_deposit(self, obj):
        for i in obj.payment_set.all():
            return [{i: i.image_path.name} for i in obj.payment_set.all()]


class HomeSerializers(serializers.ModelSerializer):
    cover = serializers.CharField()
    status = serializers.CharField(source="get_status_display")
    showtime = serializers.SerializerMethodField()
    showcommodity_set = SonSerializers(many=True)
    comm_count = serializers.SerializerMethodField()

    class Meta:
        model = models.CommodityHome
        fields = "__all__"

    def get_showtime(self, obj):
        return obj.showtime.strftime('%Y{y}%m{m}%d{d} %H{h}%M{f}%S{s}').format(y='年', m='月', d='日', h='时', f='分', s='秒')

    def get_comm_count(self, obj):
        return obj.showcommodity_set.all().count()


class DetailSerializers(SonSerializers):
    status = serializers.CharField(source="get_status_display")
    home_price = serializers.IntegerField(source="home.home_price")
    dis = serializers.SerializerMethodField()

    def get_dis(self):
        return 1


class AuctionDepositModelSerializer(serializers.ModelSerializer):
    cover = serializers.CharField()
    deposit = serializers.SerializerMethodField()
    balance = serializers.SerializerMethodField()
    pay_type = serializers.SerializerMethodField()

    class Meta:
        model = models.ShowCommodity
        fields = "__all__"

    def get_balance(self, obj):
        # 用户余额
        return self.context['request'].user.balance

    def get_deposit(self, obj):
        result = {
            "seleted": 2,
            'data_list': [
                {'id': 1, 'price': obj.payment_price, 'text': '单品保证金'},
                {'id': 2, 'price': obj.home.home_price, 'text': '全场保证金'},

            ],
            "money": obj.home.home_price,
        }
        return result

    def get_pay_type(self, obj):
        balance = self.context["request"].user.balance
        info = {
            'selected': 1,
            'choices': [
                {'id': 1, 'text': '余额（%s）' % balance},
                {'id': 2, 'text': '微信支付'},
            ]
        }
        return info


class PayDepositSerializer(serializers.Serializer):
    auction_id = serializers.IntegerField(label='拍卖ID')
    item_id = serializers.IntegerField(label='拍品ID')
    deposit_type = serializers.IntegerField(label='保证金类型')
    amount = serializers.IntegerField(label='付款金额')
    pay_type = serializers.IntegerField(label='支付方式')

    def validate_auction_id(self, value):
        """ 检查是否已支付全场保证金 """
        user_object = self.context['request'].user
        exists = models.Payment.objects.filter(auction_user=user_object, home_payment_id=value,
                                               show_Payment__isnull=True,
                                               status=2).exists()
        if exists:
            raise exceptions.ValidationError(detail='已支付过全场保证金')
        return value

    def validate_item_id(self, value):
        """ 检查是否已支付单品保证金 """
        user_object = self.context['request'].user
        exists = models.Payment.objects.filter(auction_user=user_object, show_Payment__id=value,
                                               home_payment__isnull=True, status=2).exists()
        if exists:
            raise exceptions.ValidationError(detail='已支付此单品保证金')
        return value

    def validate_deposit_type(self, value):
        # 单品保证金
        if value == 1:
            return value
        # 全场保证金，已支付过其他单品保证金，则不能再支付全场保证金。
        if value == 2:
            user_object = self.context['request'].user
            auction_id = self.initial_data.get('auction_id')
            exists = models.Payment.objects.filter(auction_user=user_object, home_payment_id=auction_id,
                                                   status=2).exists()
            if exists:
                raise exceptions.ValidationError(detail='已支付其他单品保证金，无法再支付全场保证金')
            return value
        raise exceptions.ValidationError(detail='保证金类型错误')

    def validate_amount(self, value):
        deposit_type = self.initial_data.get('deposit_type')
        print(value, type(value))

        # 单品保证金
        if deposit_type == 1:
            item_id = self.initial_data.get('item_id')
            exists = models.ShowCommodity.objects.filter(id=item_id, payment_price=value).exists()
            if not exists:
                raise exceptions.ValidationError(detail='单品保证金金额错误')
            return value

        # 全场保证金
        if deposit_type == 2:
            auction_id = self.initial_data.get('auction_id')
            exists = models.CommodityHome.objects.filter(id=auction_id, home_price=value).exists()
            if not exists:
                raise exceptions.ValidationError(detail='专场保证金金额错误')
            return value

    def validate_pay_type(self, value):
        # 微信支付
        if value == 1:
            return value

        # 余额支付，余额是否充足。
        if value == 2:
            user_object = self.context['request'].user
            amount = self.initial_data.get('amount')
            if user_object.balance < amount:
                raise exceptions.ValidationError(detail='余额不足')
            return value

        raise exceptions.ValidationError(detail='支付方式错误')


class AuctionDiscountModelSerializer(serializers.ModelSerializer):
    """
    用于优惠卷的显示
    """
    status_text = serializers.CharField(source="get_status_display", read_only=True)
    cover = serializers.CharField(read_only=True)
    auction_id = serializers.CharField(source="auction.id")
    auction = serializers.CharField(source="auction.title", read_only=True)
    end = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    start = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)
    total_count = serializers.CharField(read_only=True)
    price = serializers.CharField(read_only=True)
    use_count = serializers.CharField(read_only=True)
    remain = serializers.SerializerMethodField()

    class Meta:
        model = models.Discounts
        exclude = ["deleted", "apply_start_task_id", "apply_stop_task_id"]

    def get_remain(self, obj):
        return obj.total_count - obj.use_count


class UserDiscountModelSerializer(serializers.ModelSerializer):
    """用户展示优惠卷"""
    dis = AuctionDiscountModelSerializer()
    status_text = serializers.CharField(source="get_status_display")

    class Meta:
        model = models.Userdicount
        fields = ['dis', "ord", "status", "status_text"]


class UserAddModelSerializer(serializers.ModelSerializer):
    """
    用户添加优惠卷
    """
    # 领取的优惠卷要进行减法运算
    remain = serializers.SerializerMethodField()

    class Meta:

        model = models.Userdicount
        fields = ['dis', "ord", "remain"]

    def validate_dis(self, value):

        user_object = self.context['request'].user
        print("优惠卷的判断的值", value)
        # 优惠券不存在
        if not value or value.deleted:
            raise exceptions.ValidationError('优惠券不存在')

        # 优惠券状态必须是领取中
        if value.status != 2:
            raise exceptions.ValidationError('优惠券不可领取')

        # 优惠券个数是否合法
        if (value.use_count + 1) > value.total_count:
            raise exceptions.ValidationError('优惠券已领完')

        # 是否已领取优惠券
        exists = models.Userdicount.objects.filter(user=user_object, dis=value).exists()
        if exists:
            raise exceptions.ValidationError('优惠券已经领取过，不可重复领取')

        return value

    def get_remain(self, obj):
        return obj.discount.total_count - obj.discount.use_count - 1


class OrderShowModelSerializer(serializers.ModelSerializer):
    dis = serializers.CharField(source="discountsrecord.dis.title", read_only=True)
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M")
    # address = serializers.SerializerMethodField(read_only=True)
    item = serializers.SerializerMethodField()
    auction = serializers.CharField(source="item.home.title")

    class Meta:
        model = models.Order
        fields = ["status", "pay_type", "uid", "user", "item", "deposit", "price", "real_price", "deposit_price",
                  "address", "create_date", "dis", "auction"]

    # def get_address(self, obj):
    #     return model_to_dict(obj.address, ["name", "phone"])
    def get_item(self, obj):
        text = {
            "cover": obj.item.cover.name,
            "title": obj.item.title
        }
        return text


class OrderDetailModelSerilizer(serializers.ModelSerializer):
    deposit = serializers.SerializerMethodField()
    item = serializers.SerializerMethodField()
    create_date = serializers.DateTimeField(format="%Y-%m-%d %H:%M", read_only=True)

    # 支付方式
    pay_type = serializers.SerializerMethodField()
    # 是否有优惠卷
    discount = serializers.SerializerMethodField()

    class Meta:
        model = models.Order
        exclude = ["address", "user"]

    def get_item(self, obj):
        text = {
            "cover": obj.item.cover.name,
            "title": obj.item.title,
            "auction": obj.item.home.id
        }
        return text

    def get_deposit(self, obj):
        text = {
            "checked": False,
            "deposit_id": obj.deposit.id,
            "balance": obj.deposit.balance,
            "amount": obj.deposit.amount,
            "deposit_type_id": obj.deposit.deposit_type,
        }
        return text

    def get_pay_type(self, obj):
        balance = self.context["request"].user.balance
        info = {
            'selected': 1,
            'choices': [
                {'id': 1, 'text': '余额（%s）' % balance},
                {'id': 2, 'text': '微信支付'},
            ]
        }
        return info

    def get_discount(self, obj):
        user_object = self.context["request"].user
        exists = models.Userdicount.objects.filter(user=user_object, dis__auction_id=obj.item.home.id,
                                                   status=1).exists()
        context = {
            'id': None,
            'has': exists,
            'text': '请选择优惠券' if exists else '无',
            'money': 0
        }
        return context


class ChooseDisModelSerilizer(serializers.ModelSerializer):
    dis = serializers.SerializerMethodField()
    user = serializers.SerializerMethodField()
    status = serializers.CharField(source="get_status_display")

    class Meta:
        model = models.Userdicount
        exclude = ["ord"]

    def get_user(self, obj):
        return obj.user.nickName

    def get_dis(self, obj):
        dis = {
            "name": obj.dis.name,
            "price": obj.dis.price
        }
        return dis
