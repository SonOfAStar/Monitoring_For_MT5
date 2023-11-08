from django.db import connection
from req_reciever.models import Robot

import asyncio
import websockets
import json
import re
from asgiref.sync import sync_to_async

from . import settings


def StartAllRobots():
    """
        Получаем список всех активных роботов.
        Запускаем все роботы из списка
    """

    result = True

    robot_obj_list = GetActiveRobotList()

    for robot_obj in robot_obj_list:
        if not StartStopRobot(robot_obj.id, 'startRobot'):
            result = False

    return result

def StopAllRobots():
    """
        Получаем список всех активных роботов.
        Определяем список уникальных аккаунтов, на которых запущены активные роботы
        Останавливаем все роботы во всех аккаунтах
    """
    robot_obj_list = GetActiveRobotList()
    account_obj_list = set()

    # устанавливаем статус робота и добавляем account в список уникальных аккаунтов для отправки сообщений
    for robot_obj in robot_obj_list:
        if not SetRobotStatus(robot_obj.id, 'stopRobot'):
            return False
        account_obj_list.add(robot_obj.account)

    # для каждого аккаунта отправляем команду остановить всех роботов
    for account_obj in account_obj_list:
        message_out = createMessageStopAllRobots(account_obj.name)
        if message_out is None:
            return False
        sync_to_async(asyncio.run(ConnectAndSendMessage(message_out)))

    return True


def StartStopRobot(robot_id, robot_cmd):

    if not SetRobotStatus(robot_id, robot_cmd):
        return False

    message_out = createMessageStartStopRobot(robot_id, robot_cmd)
    if message_out is None:
        return False

    sync_to_async(asyncio.run(ConnectAndSendMessage(message_out)))
    return True


def createMessageStartStopRobot(robot_id, robot_cmd):

    # print('robot_id={}, robot_cmd={}'.format(robot_id, robot_cmd))

    with connection.cursor() as cursor:
        # drop tmp databases
        query = "DROP TABLE IF EXISTS tmp_settings;"
        # print(query)
        cursor.execute(query)

        # tmp_settings
        query = "CREATE TEMPORARY TABLE tmp_settings " \
                "SELECT " \
                "	settings.id as settings_id, " \
                "	settings.template_file as chart_settings, " \
                "	symbols.name as symbol_name, " \
                "	timeframes.name as period_name " \
                "FROM req_reciever_setting as settings " \
                "LEFT JOIN req_reciever_symbol as symbols ON settings.symbol_id=symbols.id " \
                "LEFT JOIN req_reciever_timeframe as timeframes ON settings.timeframe_id=timeframes.id;"
        # print(query)
        cursor.execute(query)

        query = "SELECT " \
                "	robots.id as robot_id, " \
                "    robots.name as robot_name, " \
                "    accounts.name as account_name, " \
                "    tmp_settings.symbol_name as symbol_name, " \
                "    tmp_settings.period_name as period_name, " \
                "    tmp_settings.chart_settings as chart_settings " \
                "FROM req_reciever_robot as robots " \
                "LEFT JOIN req_reciever_account as accounts ON accounts.id=robots.account_id " \
                "LEFT JOIN tmp_settings  ON tmp_settings.settings_id=robots.settings_id " \
                "WHERE robots.id=%s;"
        # print(query)
        cursor.execute(query, [int(robot_id)])

        robot_info = cursor.fetchone()
        # print('robot_info:')
        # print(robot_info)

    data_message_body = dict()
    data_message_body['command'] = robot_cmd
    data_message_body['robotID'] = str(robot_info[0])
    data_message_body['robotName'] = str(robot_info[1])
    data_message_body['account'] = str(robot_info[2])
    data_message_body['symbol'] = str(robot_info[3])
    data_message_body['period'] = str(robot_info[4])
    if robot_cmd == 'startRobot':
        data_message_body['chartSettings'] = ReplaceRobotID(str(robot_info[5]),str(robot_id))

    if (data_message_body['robotID'] != str(robot_id) or
        data_message_body['robotID'] is None or
        data_message_body['robotName'] is None or
        data_message_body['account'] is None or
        data_message_body['symbol'] is None or
        data_message_body['period'] is None):

        return None

    data = dict()
    data['messageID'] = int(robot_id)
    data['messageType'] = 'request'
    data['messageCommand'] = 'sendCommand'
    data['messageAccount'] = str(settings.ROBOT_MANAGER_ACCOUNT)
    data['messageBody'] = data_message_body
    # print(data)
    return json.dumps(data)

def createMessageStopAllRobots(account_name):
    # print('account_name={}'.format(account_name))

    if (account_name is None or account_name==""):
        return None

    data_message_body = dict()
    data_message_body['command'] = 'stopAllRobots'
    data_message_body['account'] = str(account_name)

    data = dict()
    data['messageID'] = 1000    # Нужно делать механизм формарования номера сообщения
    data['messageType'] = 'request'
    data['messageCommand'] = 'sendCommand'
    data['messageAccount'] = str(settings.ROBOT_MANAGER_ACCOUNT)
    data['messageBody'] = data_message_body
    # print(data)
    return json.dumps(data)

def GetActiveRobotList():
    return Robot.objects.filter(archive=False)


def SetRobotStatus(robot_id, robot_cmd):

    try:
        robot_obj = Robot.objects.get(pk=robot_id)
        if robot_cmd == 'startRobot':
            setattr(robot_obj, 'active', True)
        elif robot_cmd == 'stopRobot':
            setattr(robot_obj, 'active', False)
        robot_obj.save()
    except Robot.DoesNotExist:
        return False

    return True

def CheckSendCommandResult(message_out, message_in):
    data_out = json.loads(message_out)
    data_in = json.loads(message_in)
    if (data_in.get('messageType') == 'response' and
        data_in.get('messageAccount') == str(settings.ROBOT_MANAGER_ACCOUNT) and
        data_in.get('messageBody').get('requestID') == data_out.get('messageID') and
        data_in.get('messageBody').get('result') is True):

        return True
    else:
        return False

async def ConnectAndSendMessage(request):
    uri = 'ws://'+str(settings.ROBOT_DISPATCHER_HOST)+':'+str(settings.ROBOT_DISPATCHER_PORT)
    async with websockets.connect(uri) as websocket:
        await websocket.send(request)
        # print('Send request: >>>>>>>')
        # print(f'{request}')

        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
        # print('Recv response <<<<<<<<')
        # print(f'{response}')


def ReplaceRobotID(str_in, robot_id):
    """ Заменяем robot_id в шаблоне графика"""
    pattern = r'Expert_RobotID=\d+'
    robot_param_str = 'Expert_RobotID={}'.format(str(robot_id))
    str_out = re.sub(pattern, robot_param_str, str(str_in))
    return str_out