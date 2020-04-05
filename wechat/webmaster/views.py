import uuid
from django.shortcuts import render, redirect, HttpResponse, reverse
from django.http import JsonResponse
from django.views import View
from .Myform import myfrom
from auction import models
from django.views.decorators.csrf import csrf_exempt
from utils.upload1 import upload
from . import task
from celery.result import AsyncResult
import json
import datetime
from untitled import celery_app


# Create your views here.

def gethome(request):
    from_obj = models.CommodityHome.objects.all()
    print(from_obj)
    return render(request, "home.html", {"from_obj": from_obj})


def addedithome(request, pk=None):
    # id = request.GET.get("id")
    # print("id值", id)
    label = "编辑" if pk else "增加"
    old_obj = models.CommodityHome.objects.filter(pk=pk).first()
    if request.method == "GET":
        if pk:
            from_obj = myfrom.HomeModelForm(instance=old_obj)
            print(from_obj)
            return render(request, "edtior_add.html", {"label": label, "from_obj": from_obj, "old_obj": old_obj})
        else:
            from_obj = myfrom.HomeModelForm()
            print(from_obj)
            return render(request, "add.html", {"label": label, "from_obj": from_obj})
    else:
        print(request.POST)
        # old_obj = models.CommodityHome.objects.filter(pk=id).first()
        from_obj = myfrom.HomeModelForm(instance=old_obj, files=request.FILES, data=request.POST)
        if from_obj.is_valid():
            # print(from_obj.cleaned_data)
            instance = from_obj.save()
            preview_utc_datetime = datetime.datetime.utcfromtimestamp(instance.showtime.timestamp())
            print(preview_utc_datetime)
            preview_task_id = task.to_preview_status_task.apply_async(args=[instance.id], eta=preview_utc_datetime).id
            auction_utc_datetime = datetime.datetime.utcfromtimestamp(instance.opentime.timestamp())
            print(auction_utc_datetime)
            auction_task_id = task.to_auction_status_task.apply_async(args=[instance.id], eta=auction_utc_datetime).id
            auction_end_utc_datetime = datetime.datetime.utcfromtimestamp(instance.closetime.timestamp())
            print(auction_end_utc_datetime)
            auction_end_task_id = task.end_auction_task.apply_async(args=[instance.id], eta=auction_end_utc_datetime).id

            models.AuctionTask.objects.create(
                auction=instance,
                preview_task=preview_task_id,
                auction_task=auction_task_id,
                auction_end_task=auction_end_task_id,
            )
            return JsonResponse({"status": True})
        else:
            print("打印错误", from_obj.errors)
            return render(request, "edtior_add.html", {"label": label, "from_obj": from_obj})


"""
"""


def delete(request):
    id = request.POST.get("id")
    old_obj = models.CommodityHome.objects.all().filter(pk=id).delete()
    old_obj["status"] = True
    return render(request, {"from_obj": old_obj})


def auction_item_list(request, auction_id):
    """
    专场详细页面展示
    :param request:
    :param auction_id:
    :return:
    """
    auction_object = models.CommodityHome.objects.filter(pk=auction_id).first()
    item_list = models.ShowCommodity.objects.filter(home=auction_object)
    context = {
        "auction_object": auction_object,
        "item_list": item_list,
    }
    return render(request, "auction_item_list.html", context)


@csrf_exempt  # 用于cdrf认证跨站请求伪造
def auction_item_add(request, auction_id):
    """
    拍品添加
    :param request:
    :return:
    """
    auction_object = models.CommodityHome.objects.filter(pk=auction_id).first()
    if request.method == "GET":
        form_obj = myfrom.Item_Add_Editor()
        context = {
            'form': form_obj,
            'auction_object': auction_object
        }
        return render(request, 'auction_item_add.html', context)
    else:
        form_obj = myfrom.Item_Add_Editor(data=request.POST, files=request.FILES)
        if form_obj.is_valid():
            form_obj.instance.home = auction_object
            form_obj.instance.uid = datetime.datetime.now().strftime('%Y%m%d%H%M%S%f')
            instance = form_obj.save()

            return JsonResponse({
                'status': True,  # 添加成功
                # data是对应的url进行传参使用的
                # reverse里面有kwargs进行传参
                'data': {
                    'detail_url': reverse('webmaster:auction_item_detail_add', kwargs={'item_id': instance.id}),
                    'image_url': reverse('webmaster:auction_item_image_add', kwargs={'item_id': instance.id}),
                    'list_url': reverse('webmaster:auction_item_list', kwargs={'auction_id': auction_id})
                }
            })


def auction_item_edit(request, auction_id, item_id):
    """
    编辑页面
    :param request:
    :param auction_id:
    :param item_id:对应的拍品id
    :return:
    """
    item_object = models.ShowCommodity.objects.filter(id=item_id).first()
    detail_object_list = models.AuctionItemDetail.objects.filter(item=item_object)
    image_object_list = models.DetailCommodityPic.objects.filter(show_image=item_object)
    context = {
        "item_object": item_object,
        "detail_object_list": detail_object_list,
        "image_object_list": image_object_list
    }

    if request.method == 'GET':
        form = myfrom.Item_Add_Editor(instance=item_object)
    else:
        print(request.POST)
        print(request.FILES)
        form = myfrom.Item_Add_Editor(instance=item_object, data=request.POST, files=request.FILES)
        if form.is_valid():
            form.save()
    context['form'] = form
    print("xxx", context)
    return render(request, 'auction_item_edit.html', context)


def auction_item_delete(request, item_id):
    models.AuctionItemDetail.objects.filter(id=item_id).delete()
    return JsonResponse({'status': True})


@csrf_exempt
def auction_item_detail_add(request, item_id):
    """
    创建规格
    :param request:
    :return:
    """
    detail_list = json.loads(request.body.decode('utf-8'))
    object_list = [models.AuctionItemDetail(**info, item_id=item_id) for info in detail_list if all(info.values())]
    models.AuctionItemDetail.objects.bulk_create(object_list)
    return JsonResponse({'status': True})


@csrf_exempt
def auction_item_detail_add_one(request, item_id):
    """
    添加规则
    :param request:
    :param item_id:
    :return:
    """
    if request.method != 'POST':
        return JsonResponse({'status': False})
    form = myfrom.AuctionDetailModelForm(data=request.POST)
    if form.is_valid():
        form.instance.item_id = item_id
        instance = form.save()
        return JsonResponse({'status': True, 'data': {'id': instance.id}})
    return JsonResponse({'status': False, 'errors': form.errors})


@csrf_exempt
def auction_item_detail_delete_one(request):
    detail_id = request.GET.get('detail_id')
    models.AuctionItemDetail.objects.filter(id=detail_id).delete()
    return JsonResponse({'status': True})


@csrf_exempt
def auction_item_image_add(request, item_id):
    """
    创建图片
    :param request:
    :param item_id:
    :return:
    """
    show_list = request.POST.getlist('show')
    image_object_list = request.FILES.getlist('img')
    orm_object_list = []
    for index in range(len(image_object_list)):
        image_object = image_object_list[index]
        if not image_object:
            continue
        ext = image_object.name.rsplit('.', maxsplit=1)[-1]
        file_name = "{0}.{1}".format(str(uuid.uuid4()), ext)
        cos_path = upload(image_object, file_name)
        orm_object_list.append(
            models.DetailCommodityPic(image_path=cos_path, show_image_id=item_id, carousel=bool(show_list[index])))
    if orm_object_list:
        models.DetailCommodityPic.objects.bulk_create(orm_object_list)
    return JsonResponse({'status': True})


@csrf_exempt
def auction_item_image_add_one(request, item_id):
    print(request.POST)
    print(request.FILES)
    form = myfrom.AuctionItemImageModelForm(data=request.POST, files=request.FILES)
    if form.is_valid():
        form.instance.show_image_id = item_id
        instance = form.save()
        return JsonResponse({'status': True, 'data': {'id': instance.id}})
    print(form.errors)
    return JsonResponse({'status': False, 'errors': form.errors})


def auction_item_image_delete_one(request):
    image_id = request.GET.get('image_id')
    models.DetailCommodityPic.objects.filter(id=image_id).delete()
    return JsonResponse({'status': True})


def discount(request):
    form_obj = models.Discounts.objects.all()
    return render(request, "discount.html", {"form_obj": form_obj})


class discountadd(View):
    def get(self, request):
        label = "添加"
        from_obj = myfrom.DiscountModelForm()
        return render(request, "discount_add.html", {"from_obj": from_obj, "label": label})

    def post(self, request):
        disconut_obj = myfrom.DiscountModelForm(data=request.POST, files=request.FILES)
        if disconut_obj.is_valid():
            # 获取数据库的保存时间
            instance = disconut_obj.save()
            # 修改utc时间
            start_apply_datetime = datetime.datetime.utcfromtimestamp(disconut_obj.instance.start.timestamp())
            # 调用使用task 取到回执id
            start_task_id = task.apply_start_discount.apply_async(args=[instance.id], eta=start_apply_datetime).id

            stop_apply_datetime = datetime.datetime.utcfromtimestamp(disconut_obj.instance.start.timestamp())
            # 调用使用task 取到回执id
            stop_task_id = task.apply_stop_discount.apply_async(args=[instance.id], eta=stop_apply_datetime).id
            models.Discounts.objects.create(
                apply_start_task_id=start_task_id,
                apply_stop_task_id=stop_task_id,
            )
            return JsonResponse({'status': True})


class discountedit(View):

    def get(self, request, pk):
        label = "编辑"
        old_obj = models.Discounts.objects.filter(pk=pk).first()
        if not old_obj or old_obj.status != 1:
            return HttpResponse('优惠卷不存在或者已编辑')

        from_obj = myfrom.DiscountModelForm(instance=old_obj)
        return render(request, "discount_editor.html", {"from_obj": from_obj, "label": label, "old_obj": old_obj})

    def post(self, request, pk):
        old_obj = models.Discounts.objects.filter(pk=pk).first()
        disconut_obj = myfrom.DiscountModelForm(instance=old_obj, data=request.POST, files=request.FILES)
        if disconut_obj.is_valid():
            if "start" in disconut_obj.changed_data:
                async_result = AsyncResult(id=disconut_obj.apply_start_task_id, app=celery_app)
                async_result.revoke()
                eta = datetime.datetime.utcfromtimestamp(disconut_obj.instance.start.timestamp())
                start_task_id = task.apply_start_discount.apply_async(args=[disconut_obj.id], eta=eta).id
                disconut_obj.instance.apply_start_task_id = start_task_id

            if "end" in disconut_obj.changed_data:
                async_result = AsyncResult(id=disconut_obj.apply_stop_task_id, app=celery_app)
                async_result.revoke()
                eta = datetime.datetime.utcfromtimestamp(disconut_obj.instance.end.timestamp())
                start_task_id = task.apply_stop_discount.apply_async(args=[disconut_obj.id], eta=eta).id
                disconut_obj.instance.apply_stop_task_id = start_task_id
            disconut_obj.save()
            return JsonResponse({'status': True})