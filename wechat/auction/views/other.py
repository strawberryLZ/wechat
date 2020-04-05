from django.shortcuts import render
from rest_framework.generics import ListAPIView, RetrieveAPIView, CreateAPIView
from rest_framework.views import APIView
from rest_framework.filters import BaseFilterBackend
from rest_framework.authentication import BaseAuthentication
from rest_framework import exceptions
from auction import models as au
from api import models as api
from auction import myserializer
# from rest_framework.throttling import
from rest_framework import status
from rest_framework.response import Response
from auction import models
import uuid
from django.db import transaction


# Create your views here.

class HomeShow(ListAPIView):
    queryset = au.CommodityHome.objects
    serializer_class = myserializer.HomeSerializers


class DetailFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        id = request.query_params.get("detail_id")
        print(id)
        print(queryset.filter(pk=id))
        return queryset.filter(pk=id)


class UserAuthentication(BaseAuthentication):
    """  
    用户认证，用户必须先登录。  
    """
    def authenticate(self, request):
        token = request.META.get('HTTP_AUTHORIZATION', None)
        print(token)
        if not token:
            print('走token')
            raise exceptions.AuthenticationFailed("错误")
        print('xxxx')
        user_object = api.UserInfo.objects.filter(token=token).first()
        print("xxxx", user_object)
        if not user_object:
            print("走这了")
            raise exceptions.AuthenticationFailed()
        print("打印返回值", user_object, token)
        return (user_object, token)



class DetailHomeShow(ListAPIView):
    authentication_classes = [UserAuthentication, ]
    filter_backends = [DetailFilter, ]
    queryset = au.CommodityHome.objects
    serializer_class = myserializer.HomeSerializers


class DetailCommtidy(ListAPIView):
    authentication_classes = [UserAuthentication, ]
    filter_backends = [DetailFilter, ]
    queryset = au.ShowCommodity.objects
    serializer_class = myserializer.DetailSerializers


# celery
from django.shortcuts import HttpResponse
from auction.tasks import add


def create_task(request):
    print('请求来了')
    # 立即执行
    result = add.delay(2, 2)
    print('执行完毕')
    return HttpResponse(result.id)


def get_result(request):
    nid = request.GET.get('nid')
    from celery.result import AsyncResult
    # from demos.celery import app
    from untitled import celery_app
    result_object = AsyncResult(id=nid, app=celery_app)
    # print(result_object.status)
    data = result_object.get()
    return HttpResponse(data)


class DepositFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        item_id = request.query_params.get("item")
        print(item_id)
        print(queryset.filter(pk=item_id, status__in=[2, 3]))
        return queryset.filter(pk=item_id, status__in=[2, 3])


# 保证金(提交保证金)
class AuctionDepositView(ListAPIView):
    authentication_classes = [UserAuthentication, ]
    # 判断必须是拍卖中和售卖的
    queryset = au.ShowCommodity.objects
    serializer_class = myserializer.AuctionDepositModelSerializer
    filter_backends = [DepositFilter, ]


class PayDepositView(APIView):
    """ 保证金支付 """
    authentication_classes = [UserAuthentication, ]

    def post(self, request, *args, **kwargs):
        ser = myserializer.PayDepositSerializer(data=request.data, context={'request': request})
        ser.is_valid(raise_exception=True)
        item_id = ser.validated_data.pop('item_id')
        auction_id = ser.validated_data.pop('auction_id')
        pay_type = ser.validated_data['pay_type']
        deposit_type = ser.validated_data['deposit_type']
        amount = ser.validated_data['amount']
        uid = str(uuid.uuid4())
        # 1. 余额支付
        if pay_type == 2:
            with transaction.atomic():
                request.user.balance -= - amount
                request.user.save()
                models.Payment.objects.create(**ser.validated_data, status=2, uid=uid, auction_user=request.user,
                                              show_Payment_id=item_id if deposit_type == 1 else None,
                                              home_payment_id=auction_id if deposit_type == 2 else None,
                                              balance=amount
                                              )
            return Response({'msg': '余额支付成功'}, status=status.HTTP_200_OK)


# filter_queryset
# 优惠卷展示(获取优惠卷)
class DiscounrFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        id = request.user.id
        print(id)
        print(queryset.filter(user_id=id))
        return queryset.filter(user_id=id)


class myDiscounrFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        id = request.user.id
        print(id)
        print(queryset.filter(user_id=id))
        print("data", request.query_params.get("auction"))
        if request.query_params.get("auction"):
            print("传递的id", request.query_params.get("auction"))
            auction = request.query_params.get("auction")
            return queryset.filter(user_id=id, dis__auction_id=auction, status=1)
        return queryset.filter(user_id=id)


class DiscountView(ListAPIView):
    """
    # 优惠卷展示
    """

    authentication_classes = [UserAuthentication, ]
    queryset = au.Discounts.objects
    serializer_class = myserializer.AuctionDiscountModelSerializer


class UserCouponView(ListAPIView, CreateAPIView):
    """
    # 用户优惠卷添加(增加优惠卷)
    """
    authentication_classes = [UserAuthentication, ]
    queryset = au.Userdicount.objects
    filter_backends = [myDiscounrFilter, ]

    # serializer_class = myserializer.UserDiscountModelSerializer
    def perform_create(self, serializer):
        with transaction.atomic():
            discount_object = models.Discounts.objects.filter(
                id=serializer.validated_data['dis'].id).select_for_update().first()
            if (discount_object.use_count + 1) > discount_object.total_count:
                raise exceptions.ValidationError('优惠券已领完')
            discount_object.use_count += 1
            discount_object.save()
            serializer.save(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "POST":
            return myserializer.UserAddModelSerializer
        # 展示
        return myserializer.UserDiscountModelSerializer

    def list(self, *args, **kwargs):
        """
        组建数据结构
        """
        response = super().list(*args, **kwargs)
        # 因为传递前端的值需要进行res.data的处理 response.data相同效果
        print("re", response.data)
        if response.status_code != status.HTTP_200_OK:
            return response
        from collections import OrderedDict
        status_dict = OrderedDict()
        for item in models.Userdicount.status_choices:
            status_dict[item[0]] = {'text': item[1], 'child': []}

        for row in response.data:
            status_dict[row['status']]['child'].append(row)

        response.data = status_dict
        return response


class OrderShow(ListAPIView, CreateAPIView):
    authentication_classes = [UserAuthentication, ]
    queryset = au.Order.objects
    filter_backends = [DiscounrFilter, ]

    def get_serializer_class(self):

        return myserializer.OrderShowModelSerializer

    def list(self, *args, **kwargs):
        response = super().list(*args, **kwargs)
        print("x", response.data)
        if response.status_code != status.HTTP_200_OK:
            return response
        from collections import OrderedDict
        status_dict = OrderedDict()
        for index, text in models.Order.status_choices:
            status_dict[index] = {"text": text, "child": []}
        for row in response.data:
            status_dict[row["status"]]["child"].append(row)
        response.data = status_dict
        return response


class OrderDetailFilter(BaseFilterBackend):
    def filter_queryset(self, request, queryset, view):
        id = request.user.id
        print(id)
        detail_id = request.query_params.get("detail_id")
        print(queryset.filter(user_id=id, pk=detail_id))
        return queryset.filter(user_id=id, pk=detail_id)


class OrderShowdetail(ListAPIView):
    serializer_class = myserializer.OrderDetailModelSerilizer
    authentication_classes = [UserAuthentication, ]
    filter_backends = [OrderDetailFilter, ]
    queryset = models.Order.objects


class ChooseDis(ListAPIView):
    """
    # 选择优惠卷
    """
    authentication_classes = [UserAuthentication, ]
    queryset = au.Userdicount.objects
    filter_backends = [myDiscounrFilter, ]
    serializer_class = myserializer.ChooseDisModelSerilizer


class Orderpay(APIView):
    authentication_classes = [UserAuthentication, ]

    def post(self, request, *args, **kwargs):
        print(request.data)
        order_id = request.data.get("order_id")
        discount_id = request.data.get("discount_id")
        use_deposit = request.data.get("usedeposit")
        # address_id = request.data.get("address_id")
        real_pay = request.data.get("real_price")
        pay_type = request.data.get("pay_type")

        # 地址的数据校验
        # address_object=models.Address.objects.filter(user=request.user,id=address_id).first()
        # if not address_object:
        #     raise exceptions.ValidationError('地址不存在')
        with transaction.atomic():
            # 如果有就对这条查询数据进行锁定 不能进行更改
            order_object = models.Order.objects.filter(id=order_id, user=request.user,
                                                       status=1).select_for_update().first()
            if not order_object:
                return Response("没有此订单")
                # raise exceptions.ValidationError("没有此订单")
            # 原价
            price = order_object.price
            # 实际支付价格
            real_price = order_object.price
            deposit_deduct_object = None
            deposit_refund_object = None
            discount_object = None
            # 1.是否使用优惠卷
            if discount_id:
                # 从自己的优惠卷中查找优惠卷
                discount_object = models.Userdicount.objects.filter(user=request.user, status=1,
                                                                    dis_id=discount_id).first()
                if not discount_object:
                    # return Response("没有此优惠卷")
                    raise exceptions.ValidationError("没有此优惠卷")
                # 查找到优惠卷进行抵扣
                remain = price - discount_object.dis.price
                if remain > 0:
                    real_price = remain
                else:
                    real_price = 0

            # 使用保证金
            if use_deposit:

                # 全场保证金
                if order_object.deposit.deposit_type == 2:
                    # 保证金抵扣
                    remain = real_price - order_object.deposit.balance
                    print(remain)
                    # 抵扣不完写上抵扣钱数(抵扣记录) 全部抵扣
                    if remain > 0:
                        # 抵扣记录
                        deposit_deduct_object = models.DepositDeduct(
                            order_id=order_object.id,
                            amount=order_object.deposit.balance,
                            deduct_type=2
                        )
                        order_object.deposit.balance = 0
                        real_price = real_price - order_object.deposit.balance
                    else:
                        deposit_deduct_object = models.DepositDeduct(
                            order_id=order_object.id,
                            amount=real_price,
                            deduct_type=2
                        )
                        # 抵扣完开始退款
                        exists = models.Order.objects.filter(
                            item__home_id=order_object.deposit.home_payment_id,
                            user=request.user,
                            status=1
                        ).exclude(id=order_object.id).exists()
                        # 不退 保证金余额要处理
                        if exists:
                            order_object.deposit.balance = order_object.deposit.balance - real_price
                        else:
                            # 退保证金到用户余额
                            request.user.balance = request.user.balance + (order_object.deposit.balance - real_price)

                            # 退保证金记录
                            deposit_refund_object = models.DepositRefundRecord(
                                uid=str(uuid.uuid4()),
                                status=2,
                                deposit=order_object.deposit,
                                amount=order_object.deposit.balance - real_price
                            )

                            # 保证金的余额减为 0
                            order_object.deposit.balance = 0

                            # 之后付款 0
                        real_price = 0
                else:
                    remain = real_price - order_object.deposit.balance
                    if remain > 0:
                        real_price = real_price - order_object.deposit.balance
                        deposit_deduct_object = models.DepositDeduct(
                            order_id=order_object.id,
                            amount=order_object.deposit.balance,
                            deduct_type=2
                        )
                        order_object.deposit.balance = 0
                    else:
                        deposit_deduct_object = models.DepositDeduct(
                            order_id=order_object.id,
                            amount=real_price,
                            deduct_type=2
                        )
                        # 抵扣完开始退款
                        # 退保证金到用户余额
                        request.user.balance = request.user.balance + (order_object.deposit.balance - real_price)

                        # 退保证金记录
                        deposit_refund_object = models.DepositRefundRecord(
                            uid=str(uuid.uuid4()),
                            status=2,
                            deposit=order_object.deposit,
                            amount=order_object.deposit.balance - real_price
                        )

                        # 保证金的余额减为 0
                        order_object.deposit.balance = 0

                        # 之后付款 0
                        real_price = 0
                print(real_price)
            # 不使用抵扣金
            else:
                # 用户不用保证金抵扣，自己还有保证金
                # 如果原来交的是单品保证金，直接退
                # 如果来交的是全场保证金，直接退（判断还有没有当前专场其他待支付的订单）
                if order_object.deposit.balance > 0:
                    if order_object.deposit.deposit_type == 1:
                        # 单品保证金

                        # 退保证金记录
                        deposit_refund_object = models.DepositRefundRecord(
                            uid=str(uuid.uuid4()),
                            status=2,
                            deposit=order_object.deposit,
                            amount=order_object.deposit.balance
                        )
                        # 退款到原账户
                        request.user.balance = request.user.balance + order_object.deposit.balance
                        order_object.deposit.balance = 0

                    else:
                        # 全场保证金
                        exists = models.Order.objects.filter(
                            user=request.user,
                            status=1,
                            item__auction_id=order_object.deposit.auction_id).exclude(id=order_object.id).exists()
                        if not exists:
                            # 退保证金记录
                            deposit_refund_object = models.DepositRefundRecord(
                                uid=str(uuid.uuid4()),
                                status=2,
                                deposit=order_object.deposit,
                                amount=order_object.deposit.balance
                            )
                            # 退款到原账户
                            request.user.balance = request.user.balance + order_object.deposit.balance
                            order_object.deposit.balance = 0
            # ## 2.4 应付金额判断
            print({real_pay: type(real_pay), real_price: type(real_price)})
            if real_pay != real_price:
                # return Response("前端和后端支付价格不一致")
                raise exceptions.ValidationError('前端和后端支付价格不一致')

            # 3.支付
            """
            if pay_type == 1:
                # 微信支付
                #   与支付订单的ID，签名给小程序返回json数据
                #   小程序中进行支付
                #       用户支付，
                #       用不不支付
                #   将订单和各种抵扣全都处理，但订单状态 先变更为 未支付，支付中，->已支付 （回调函数）
                pass
            else:
                # 余额支付
                pass
            """

            if request.user.balance < real_price:
                return Response("余额不够，请充值")
                # raise exceptions.ValidationError('余额不够，请充值')

            # 通过余额去支付
            request.user.balance = request.user.balance - real_price

            # 4. 数据更新
            # 对订单进行修改(带收货 -> 完成 )
            models.Order.objects.filter(id=order_object.id).update(real_price=real_price, pay_type=2,
                                                                   status=3
                                                                   )
            # address_id=address_id)
            # 抵扣记录
            if deposit_deduct_object:
                deposit_deduct_object.save()
            # 退款记录
            if deposit_refund_object:
                deposit_refund_object.save()
            # 如果用了优惠券
            if discount_object:
                discount_object.save()
            # 余额退还
            request.user.save()

            # 此订单关联用户保证金余额提交数据（余额清空）
            order_object.deposit.save()

        return Response("支付成功", status=status.HTTP_200_OK)
