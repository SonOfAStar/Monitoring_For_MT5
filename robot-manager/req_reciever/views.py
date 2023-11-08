from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from .log_class import DarwintLog


@csrf_exempt
def parser(request):
    if request.method == 'GET':
        return HttpResponse('receive')
    # При посылке джсона следует проследить за правильными кавычками:
    # двойные вокруг строк, одиночные вокруг всего текста в МТ5

    # print("recieved http:",request)

    new_log = DarwintLog(request)
    # print("recieved log:", new_log)

    response = new_log.to_database()
    # print("recieved body:", request.body.decode())

    return HttpResponse(response)
