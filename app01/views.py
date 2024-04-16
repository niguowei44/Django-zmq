from django.shortcuts import render

# Create your views here.


def index(request):
    """
    1.当访问index页面时，会调用此函数，并传入request对象。
    此函数会从request对象中获取num参数，并将其传递给html模板
    会将get请求参数num的值传递给group_num变量
    然后将group_num变量传递给html模板，并渲染出页面
    :param request:
    :return:
    """
    group_num = request.GET.get('num')  # num 就是url里 http://127.0.0.1:8000/index/?num=123 的num参数
    return render(request, 'index.html', {"group_num": group_num})




