from django.contrib import admin
from auction import models as au

# Register your models here.
admin.site.register(au.CommodityHome)
admin.site.register(au.ShowCommodity)
admin.site.register(au.AuctionPayment)
admin.site.register(au.DetailCommodityPic)
admin.site.register(au.Focus)
admin.site.register(au.Payment)
admin.site.register(au.Order)
admin.site.register(au.Userdicount)
admin.site.register(au.Discounts)
