# from datetime import datetime
#
# # print(datetime.strptime('2020-01-13 03:21:00.856752',"%Y-%m-%d %H:%M:%S"))
#
# print(str(datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "untitled.settings")
django.setup()

from api import models
from random import randint
obj_list = []
for i in range(2,30):
    vis_obj =models.UserInfo(
        phone='151312555{0}'.format(i),
        nickName='子文-{0}'.format(i),
        avatarUrl='https://mini-1251317460.cos.ap-chengdu.myqcloud.com/08a9daei1578736867828.png'
    )
    obj_list.append(vis_obj)
models.UserInfo.objects.bulk_create(obj_list)

