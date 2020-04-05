# # parant_list = [
# #     {
# #         "id": 1,
# #         "content": "1",
# #         "user__nickname": "wupeiqi",
# #         "user__avatar": "aads",
# #         "create_date": "2020-01-15T07:46:35.113307Z"
# #     },
# #     {
# #         "id": 6,
# #         "content": "2",
# #         "user__nickname": "大卫-1",
# #         "user__avatar": "https://mini-1251317460.cos.ap-chengdu.myqcloud.com/08a9daei1578736867828.png",
# #         "create_date": "2020-01-15T07:46:35.527296Z"
# #     },
# #     {
# #         "id": 7,
# #         "content": "3",
# #         "user__nickname": "大卫-2",
# #         "user__avatar": "https://mini-1251317460.cos.ap-chengdu.myqcloud.com/08a9daei1578736867828.png",
# #         "create_date": "2020-01-15T07:46:35.618243Z"
# #     }
# #
# # ]
# #
# # node_list = [
# #     {
# #         "id": 5,
# #         "content": "1-2",
# #         "user__nickname": "大卫-6",
# #         "user__avatar": "https://mini-1251317460.cos.ap-chengdu.myqcloud.com/08a9daei1578736867828.png",
# #         "create_date": "2020-01-15T07:46:35.434290Z",
# #         "reply_id": 1,
# #         "reply__user__nickname": "wupeiqi"
# #     },
# #     {
# #         "id": 8,
# #         "content": "2-1",
# #         "user__nickname": "大卫-2",
# #         "user__avatar": "https://mini-1251317460.cos.ap-chengdu.myqcloud.com/08a9daei1578736867828.png",
# #         "create_date": "2020-01-15T07:46:35.618243Z",
# #         "reply_id": 6,
# #         "reply__user__nickname": "大卫-1"
# #     }
# # ]
# # for t in parant_list:
# #     for i in node_list:
# #         if i["reply_id"] == t["id"]:
# #             t.setdefault("children", {})['second'] = i
# #             print(t)
# # """
# # {
# # 	'id': 1,
# # 	'content': '1',
# # 	'user__nickname': 'wupeiqi',
# # 	'user__avatar': 'aads',
# # 	'create_date': '2020-01-15T07:46:35.113307Z',
# # 	'children': {
# # 		'second': {
# # 			'id': 5,
# # 			'content': '1-2',
# # 			'user__nickname': '大卫-6',
# # 			'user__avatar': 'https://mini-1251317460.cos.ap-chengdu.myqcloud.com/08a9daei1578736867828.png',
# # 			'create_date': '2020-01-15T07:46:35.434290Z',
# # 			'reply_id': 1,
# # 			'reply__user__nickname': 'wupeiqi'
# # 		}
# # 	}
# # } {
# # 	'id': 6,
# # 	'content': '2',
# # 	'user__nickname': '大卫-1',
# # 	'user__avatar': 'https://mini-1251317460.cos.ap-chengdu.myqcloud.com/08a9daei1578736867828.png',
# # 	'create_date': '2020-01-15T07:46:35.527296Z',
# # 	'children': {
# # 		'second': {
# # 			'id': 8,
# # 			'content': '2-1',
# # 			'user__nickname': '大卫-2',
# # 			'user__avatar': 'https://mini-1251317460.cos.ap-chengdu.myqcloud.com/08a9daei1578736867828.png',
# # 			'create_date': '2020-01-15T07:46:35.618243Z',
# # 			'reply_id': 6,
# # 			'reply__user__nickname': '大卫-1'
# # 		}
# # 	}
# # }
# # """
# import os
# import sys
# import django
#
# base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# sys.path.append(base_dir)
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "untitled.settings")
# django.setup()
#
# from api import models
#
# # ########################## 创建三条根评论 ##########################
# first1 = models.Comment.objects.create(
#     article_id=28,
#     content="1",
#     user_id=1,
#     depth=1
# )
#
# first1_1 = models.Comment.objects.create(
#     article_id=28,
#     content="1-1",
#     user_id=6,
#     reply=first1,
#     depth=2,
#     root=first1
# )
#
# first1_1_1 = models.Comment.objects.create(
#     article_id=28,
#     content="1-1-1",
#     user_id=10,
#     reply=first1_1,
#     depth=3,
#     root=first1
# )
# first1_1_2 = models.Comment.objects.create(
#     article_id=28,
#     content="1-1-2",
#     user_id=14,
#     reply=first1_1,
#     depth=3,
#     root=first1
# )
#
#
# first1_2 = models.Comment.objects.create(
#     article_id=28,
#     content="1-2",
#     user_id=8,
#     reply=first1,
#     depth=2,
#     root=first1
# )
#
#
# first2 = models.Comment.objects.create(
#     article_id=28,
#     content="2",
#     user_id=3,
#     depth=1
# )
#
# first3 = models.Comment.objects.create(
#     article_id=28,
#     content="3",
#     user_id=4,
#     depth=1
# )1

parent_list = [
{
    "id": 1,
    "content": "1",
    "user__nickname": "wupeiqi",
    "user__avatar": "aads",
    "create_date": "2020-01-15T07:46:35.113307Z"
},
{
    "id": 6,
    "content": "2",
    "user__nickname": "大卫-1",
    "user__avatar": "https://mini-1251317460.cos.ap-chengdu.myqcloud.com/08a9daei1578736867828.png",
    "create_date": "2020-01-15T07:46:35.527296Z"
},
{
    "id": 7,
    "content": "3",
    "user__nickname": "大卫-2",
    "user__avatar": "https://mini-1251317460.cos.ap-chengdu.myqcloud.com/08a9daei1578736867828.png",
    "create_date": "2020-01-15T07:46:35.618243Z"
}

]

node_list = [
    {
        "id": 5,
        "content": "1-2",
        "user__nickname": "大卫-6",
        "user__avatar": "https://mini-1251317460.cos.ap-chengdu.myqcloud.com/08a9daei1578736867828.png",
        "create_date": "2020-01-15T07:46:35.434290Z",
        "reply_id": 1,
        "reply__user__nickname": "wupeiqi"
    },
    {
        "id": 8,
        "content": "2-1",
        "user__nickname": "大卫-2",
        "user__avatar": "https://mini-1251317460.cos.ap-chengdu.myqcloud.com/08a9daei1578736867828.png",
        "create_date": "2020-01-15T07:46:35.618243Z",
        "reply_id": 6,
        "reply__user__nickname": "大卫-1"
    }
]


# 第一步：构造字典
parent_dict = {}
for item in parent_list:
    parent_dict[item['id']] = item

# 第二步：往字典中添加至
for node in node_list:
    parent_id = node['reply_id']
    parent_dict[parent_id]['child'] = [node,]

print(parent_dict)