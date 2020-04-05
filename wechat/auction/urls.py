from django.conf.urls import url
from auction.views import other

urlpatterns = [
    # 获取首页
    url(r"^home$", other.HomeShow.as_view()),
    url(r"^detailihome$", other.DetailHomeShow.as_view()),
    # 拍卖详细
    url(r"^detailcommtidy$", other.AuctionDepositView.as_view()),
    # celery测试
    url(r'^create/task/$', other.create_task),
    url(r'^get/result/$', other.get_result),
    #保证金
    url(r'^creat/deposit/$', other.PayDepositView.as_view()),
    # 所有优惠卷的获取
    url(r'^discount/show$', other.DiscountView.as_view()),

    # 用户优惠卷的增加和查询
    url(r'^discount/user$', other.UserCouponView.as_view()),

    # 用户订单状态查询
    url(r"^order/user$", other.OrderShow.as_view()),
    url(r"^order/detail$", other.OrderShowdetail.as_view()),
    # 订单对应的专场优惠卷
    url(r"^order/discount$", other.ChooseDis.as_view()),
    url(r"^order/pay$", other.Orderpay.as_view())
]
