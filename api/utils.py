# -*- encoding: utf-8 -*-
#
# comment
#
# 2017/1/15 0015 Jay : Init

from django.http import JsonResponse

def render_json(result=True, data=None, message=None, status=200, extra_params=None):
    response_data = {
        "result": result,
        "data": data,
        "message": message,
    }
    if extra_params and isinstance(extra_params, dict):
        response_data.update(extra_params)

    return JsonResponse(data=response_data, status=status)

