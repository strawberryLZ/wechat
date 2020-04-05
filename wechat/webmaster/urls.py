# url
from django.conf.urls import url
from webmaster import views

urlpatterns = [
    # 拍卖专场
    url(r"^home$", views.gethome, name="home"),
    url(r"^add_editor$", views.addedithome, name="add"),
    url(r"^add_editor/(?P<pk>\d+)/$", views.addedithome, name="editor"),
    url(r"^del$", views.delete, name='del'),

    # 专场详细拍品列表
    url(r"^auction_item_list/(?P<auction_id>\d+)$", views.auction_item_list, name='auction_item_list'),
    url(r"^auction_item_add/(?P<auction_id>\d+)$", views.auction_item_add, name='auction_item_add'),
    # url(r"^upload$", views.addedithome, name='upload'),
    url(r'^auction/item/edit/(?P<auction_id>\d+)/(?P<item_id>\d+)/$', views.auction_item_edit,
        name='auction_item_edit'),
    url(r'^auction/item/delete/(?P<item_id>\d+)/$', views.auction_item_delete, name='auction_item_delete'),

    # 拍品详细
    url(r'^auction/item/detail/add/(?P<item_id>\d+)/$', views.auction_item_detail_add, name='auction_item_detail_add'),
    url(r'^auction/item/detail/add/one/(?P<item_id>\d+)/$', views.auction_item_detail_add_one,
        name='auction_item_detail_add_one'),
    url(r'^auction/item/detail/delete/one/$', views.auction_item_detail_delete_one,
        name='auction_item_detail_delete_one'),
    url(r'^auction/item/image/add/(?P<item_id>\d+)/$', views.auction_item_image_add, name='auction_item_image_add'),
    url(r'^auction/item/image/add/one/(?P<item_id>\d+)/$', views.auction_item_image_add_one,
        name='auction_item_image_add_one'),
    url(r'^auction/item/image/delete/one/$', views.auction_item_image_delete_one, name='auction_item_image_delete_one'),
    # 优惠卷
    url(r"^discount/show$", views.discount, name='getdicount'),
    url(r"^discount/add$", views.discountadd.as_view(), name='dicountadd'),
    url(r"^discount/editor$", views.discountedit.as_view(), name='dicounteditor'),

]
