from django.http import HttpResponse

from .dispatcher_app import StopAllRobots, StartAllRobots, StartStopRobot

# Create your views here.
def send_cmd_view(request):
    # print("Start send_cmd_view!")
    # print(request.POST)
    robot_id = request.POST.get('robot_id')
    robot_cmd = request.POST.get('robot_cmd')

    result = True

    if robot_cmd == 'stopAllRobots':
        result = StopAllRobots()
    elif robot_cmd == 'startAllRobots':
        result = StartAllRobots()
    elif robot_cmd == 'startRobot' and robot_id != '0':
        result = StartStopRobot(robot_id, robot_cmd)
    elif robot_cmd == 'stopRobot' and robot_id != '0':
        result = StartStopRobot(robot_id, robot_cmd)
    else:
        result = False

    response_str = "Send robot command: {}\n ".format(robot_cmd)
    if (result is True):
        response_str += "Result: Successful"
    else:
        response_str += "Result: Unsuccessful"

    return HttpResponse(response_str)

