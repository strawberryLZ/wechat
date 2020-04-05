from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response


class OldBoyLimitPagination(LimitOffsetPagination):
    """
    本质上帮助我们进行切片的处理：[0:N]
    """
    default_limit = 5  # 显示5条
    max_limit = 50
    limit_query_param = 'limit'  # 参数
    offset_query_param = 'offset'

    def get_offset(self, request):
        return 0  # 从0开始

    def get_paginated_response(self, data):
        return Response(data)
