import datetime


#
# Класс, описывающий структуру и логику вывода данных из БД в таблицу монитора,
# ОСНОВНЫЕ МОМЕНТЫ -
#   парсинг списка в объект класса,
#   логика цветовой подсказки,
#   сортировка на основе приоритетов решения проблем
#

# получаемая последовательность столбцов
# | id | db_robot_name | active | archive
# | db_symbol | symbol_end | db_params | db_timeframe | tf_minutes
# | cluster | robot_version | account | owner | broker
# | market_schedule | mon | tue | wed | thu | fri | sat | sun
# | ini_account | ini_params | ini_version | ini_time | ini_signal | ini_symbol | ini_timeframe
# | msg_trading_enabled | limit_orders | volume | msg_time | msg_symbol | msg_timeframe | msg_account |

class MonitorRow:
    def __init__(self, input_query=[]):
        self.data = {}
        if len(input_query) != 37:
            self.data['id'] = 0
            self.data['name'] = "Empty row"
            self.data['active'] = True
            self.data['archive'] = False
            self.data['db_symbol'] = "--no data--"
            self.data['symbol_end'] = datetime.date.today()
            self.data['db_params'] = "--no data--"
            self.data['db_timeframe'] = "--no data--"
            self.data['db_tf_minutes'] = "--no data--"
            self.data['cluster'] = "--no data--"
            self.data['robot_version'] = "--no data--"
            self.data['db_account'] = -1
            self.data['owner'] = "--no data--"
            self.data['broker'] = "--no data--"
            self.data['market_schedule'] = "--no data--"
            self.data['mon'] = False
            self.data['tue'] = False
            self.data['wed'] = False
            self.data['thu'] = False
            self.data['fri'] = False
            self.data['sat'] = False
            self.data['sun'] = False

            self.data['ini_account'] = 0
            self.data['ini_params'] = "--no data--"
            self.data['ini_version'] = "--no data--"
            self.data['ini_trading_enabled'] = 0
            self.data['ini_time'] = datetime.datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)
            self.data['ini_symbol'] = "--no data--"
            self.data['ini_signal'] = "--no data--"
            self.data['ini_timeframe'] = "--no data--"

            self.data['msg_trading_enabled'] = 0
            self.data['msg_limit_orders'] = 0
            self.data['msg_volume'] = 0.00
            self.data['msg_time'] = datetime.datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)
            self.data['msg_symbol'] = "--no data--"
            self.data['msg_timeframe'] = "--no data--"
            self.data['msg_account'] = 0

            self.data['commentary'] = ""
            self.data['is_demo'] = False

        else:

            self.data['id'] = input_query[0] if not input_query[0] is None else -1
            self.data['name'] = input_query[1] if not input_query[1] is None else "--no data--"
            self.data['active'] = input_query[2] if not input_query[2] is None else False
            self.data['archive'] = input_query[3] if not input_query[3] is None else False
            self.data['db_symbol'] = input_query[4] if not input_query[4] is None else "--no data--"
            self.data['symbol_end'] = input_query[5] if not input_query[5] is None else datetime.date.today()
            self.data['db_params'] = input_query[6] if not input_query[6] is None else "--no data--"
            self.data['db_timeframe'] = input_query[7] if not input_query[7] is None else "--no data--"
            self.data['db_tf_minutes'] = input_query[8] if not input_query[8] is None else "--no data--"
            self.data['cluster'] = input_query[9] if not input_query[9] is None else "--no data--"
            self.data['robot_version'] = input_query[10] if not input_query[10] is None else "--no data--"
            self.data['db_account'] = str(input_query[11]) if not input_query[11] is None else 0
            self.data['owner'] = input_query[12] if not input_query[12] is None else "--no data--"
            self.data['broker'] = input_query[13] if not input_query[13] is None else "--no data--"
            self.data['market_schedule'] = input_query[14] if not input_query[14] is None else "--no data--"
            self.data['mon'] = input_query[15] if not input_query[15] is None else False
            self.data['tue'] = input_query[16] if not input_query[16] is None else False
            self.data['wed'] = input_query[17] if not input_query[17] is None else False
            self.data['thu'] = input_query[18] if not input_query[18] is None else False
            self.data['fri'] = input_query[19] if not input_query[19] is None else False
            self.data['sat'] = input_query[20] if not input_query[20] is None else False
            self.data['sun'] = input_query[21] if not input_query[21] is None else False

            self.data['ini_account'] = input_query[22] if not input_query[22] is None else 0
            self.data['ini_params'] = input_query[23] if not input_query[23] is None else "--no data--"
            self.data['ini_version'] = input_query[24] if not input_query[24] is None else "--no data--"
            self.data['ini_trading_enabled'] = input_query[25] if not input_query[25] is None else 0
            self.data['ini_time'] = input_query[26] if not input_query[26] is None else datetime.datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)
            self.data['ini_signal'] = input_query[27] if not input_query[27] is None else "--no data--"
            self.data['ini_symbol'] = input_query[28] if not input_query[28] is None else "--no data--"
            self.data['ini_timeframe'] = input_query[29] if not input_query[29] is None else "--no data--"

            self.data['msg_trading_enabled'] = input_query[30] if not input_query[30] is None else 0
            self.data['msg_limit_orders'] = input_query[31] if not input_query[31] is None else 0
            self.data['msg_volume'] = float(input_query[32]) if not input_query[32] is None else 0
            self.data['msg_time'] = input_query[33] if not input_query[33] is None else datetime.datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)
            self.data['msg_symbol'] = input_query[34] if not input_query[34] is None else "--no data--"
            self.data['msg_timeframe'] = input_query[35] if not input_query[35] is None else "--no data--"
            self.data['msg_account'] = input_query[36] if not input_query[36] is None else 0

            self.data['commentary'] = ""
            self.data['is_demo'] = False

        # print(self.data['id'], " is robot")

        self.data['status'] = self.CalcStatus()
        self.data['priority'] = self.CalcPriority()
        self.data['commentary'] = self.data['commentary'].lstrip()
        self.PrintCommentary()

    def __getitem__(self, item):
        return self.data[item]

    def __lt__(self, other):
        result = False
        if self.data['priority'] < other['priority']:
            result = True
        elif self.data['priority'] == other['priority']:
            if self.data['name'] > other['name']:
                result = True
            elif self.data['id'] > other['id']:
                result = True
        return result

    def CalcStatus(self):
        #   определяет поле статуса робота
        dt_eval = self.EvaluateDateime()
        data_check = self.DataCheck()

        # print(self.data['name'], dt_eval)
        if self.data['archive']:
            if self.data['active']:
                self.data['commentary'] += "Робот необходимо выключить, чтобы отправить в архив!\n"
                return "ERR"
            elif not dt_eval:
                self.data['commentary'] += "Робот продолжает работу после отправки в архив!\n"
                return "ERR"
            return "OFF"
        elif self.data['active']:
            if dt_eval:
                if data_check:
                    if self.CheckDemo():
                        return "DEMO"
                    return "OK"
                else:
                    return "WARN"
            else:
                return "ERR"
        else:
            if dt_eval:
                return "OFF"
            else:
                return "ERR"


    def CalcPriority(self):
        # определяет степень важности робота, влияет на сортировку, чем ниже priority - тем выше расположить при выводе
        priority = 0

        if self.data['status'] == "WARN":
            priority += 2
        if self.data['status'] == "OK":
            priority += 4
        if self.data['status'] == "DEMO":
            priority += 6
        if self.data['status'] == "OFF":
            priority += 8

        if self.data['msg_volume'] != 0:
            priority -= 1
        # print(type(priority),priority, self.data['name'])

        return priority


    def EvaluateDateime(self):

        dt_now = datetime.datetime.now()

        # print("comparing ", self.data['msg_time'], " --- to now --- ", dt_now)

        if self.data['active']:

            if self.data['ini_signal'] != "on":
                self.data['commentary'] += "Активный робот не прислал сообщение on!\n"
                return False

            self.GetActualIntervals(dt_now)
            return self.CheckLastBar(dt_now)

        else:
            if self.data['ini_signal'] != "off":
                self.data['commentary'] += "Остановленный робот не прислал сообщение off!\n"
                return False
            if self.data['ini_time'] >= self.data['msg_time']:
                # print(self.data['ini_time'], "---", dt_now)
                if self.data['ini_time'] < dt_now:
                    return True
            # print(self.data['ini_time'], "---", self.data['msg_time'])
            return False

    def GetActualIntervals(self, dt_now):

        dt_now_start = dt_now.replace(hour=0, minute=0, second=0, microsecond=0)

        self.data['any_timedelta'] = False

        days = []
        if self.data['mon']:
            days.append(0)
        if self.data['tue']:
            days.append(1)
        if self.data['wed']:
            days.append(2)
        if self.data['thu']:
            days.append(3)
        if self.data['fri']:
            days.append(4)
        if self.data['sat']:
            days.append(5)
        if self.data['sun']:
            days.append(6)
        # print(days)

        split_schedule = self.data['market_schedule'].split("\n")
        intervals = []
        for elem in split_schedule:
            times = elem.split("-")
            converted_times = [datetime.datetime.strptime(times[0].rstrip().lstrip(), '%H.%M'),
                               datetime.datetime.strptime(times[1].rstrip().lstrip(), '%H.%M')]
            intervals.append(converted_times)

        # print(intervals)

        if len(days) == 0 or len(intervals) == 0:
            # Если у биржи нет рабочих дней или не определены рабочие часы,
            # любое время последнего сообщения будет корректным.
            self.data['any_timedelta'] = True
            return

        max_timedelta = datetime.timedelta(days=0)
        dt_end_of_day = intervals[-1][1].replace(hour=23, minute=59, second=59)

        if dt_now.weekday() in days:
            # print("weekday working")
            left_border = dt_now_start
            right_border = intervals[0][0]
            interval_idx = -1

            for i in range(0,len(intervals)+1):
                # print("n:",dt_now.time(),"l:",left_border.time(),"r:",right_border.time())
                if dt_now.time() < left_border.time():
                    # print("to left")
                    interval_idx = i - 1
                    break
                if dt_now.time() <= right_border.time():
                    # print("to right")
                    break
                if i+1 <= len(intervals)-1:
                    left_border = intervals[i][1]
                    right_border = intervals[i+1][0]
                elif i+1 == len(intervals):
                    left_border = intervals[i][1]
                    right_border = dt_end_of_day

            if interval_idx >= 0:
                interval_start = intervals[interval_idx][0].replace(year=dt_now.year,
                                                                    month=dt_now.month, day=dt_now.day)
                if dt_now - interval_start < datetime.timedelta(minutes=1+self.data['db_tf_minutes']):
                    if interval_idx == 0:
                        max_timedelta += dt_now - dt_now_start
                        day = (dt_now.weekday() + 6) % 7
                        # print(max_timedelta)

                        while not (day in days):
                            day = (day + 6) % 7
                            max_timedelta += datetime.timedelta(days=1)

                        last_interval_end = intervals[-1][1]
                        max_timedelta += dt_end_of_day - last_interval_end
                        # print(max_timedelta)
                    else:
                        max_timedelta += intervals[interval_idx][0] - intervals[interval_idx - 1][1]
                        # print(max_timedelta)
            else:

                interval_start = left_border.replace(year=dt_now.year, month=dt_now.month, day=dt_now.day)
                max_timedelta += dt_now - interval_start
                # print(interval_start, " to today ",dt_now)
                # print(left_border,":l, r:",right_border)
                #
                # print(max_timedelta)

        else:
            # print("Holiday, calculating timedelta to the start of the day.")
            max_timedelta += dt_now - dt_now_start
            # print(max_timedelta)
            day = (dt_now.weekday() + 6) % 7
            # print(day+1, max_timedelta)

            while not (day in days):
                day = (day + 6) % 7
                max_timedelta += datetime.timedelta(days=1)
                # print(day, max_timedelta)

            last_interval_end = intervals[-1][1]
            max_timedelta += dt_end_of_day - last_interval_end
            # print(max_timedelta)

        max_timedelta += datetime.timedelta(minutes=1+self.data['db_tf_minutes'])

        self.data['max_timedelta'] = max_timedelta
        # print(max_timedelta)

    def CheckLastBar(self, dt_now):

        if self.data['any_timedelta']:
            # print("Any timedelta would work!")
            return True

        if self.data['ini_time'] < self.data['msg_time']:
            if self.data['msg_time'] + self.data['max_timedelta'] >= dt_now:
                return True
            else:
                return False
        else:
            if self.data['ini_time'] + self.data['max_timedelta'] >= dt_now:
                return True
            else:
                return False

    def PrintTime(self):
        pass

    def DataCheck(self):

        symb = self.CheckSymbol()
        expiration = self.CheckExpiration()
        tf = self.CheckTimeframe()
        account = self.CheckAccount()
        params = self.CheckParams()
        permissions = self.CheckPermissions()
        version = self.CheckVersion()

        return symb and params and tf and account and permissions and expiration and version


    def PrintCommentary(self):
        self.data['commentary_snapshot'] = self.data['commentary'].split("\n")[0]
        if len(self.data['commentary']) > len(self.data['commentary_snapshot'])+1:
            self.data['commentary_snapshot'] += "..."


    def CheckSymbol(self):
        if self.data['msg_time'] > self.data['ini_time']:
            if self.data['db_symbol'] != self.data['msg_symbol']:
                self.data['commentary'] += "Неверный инструмент!\n" \
                                           " Запущен на " + self.data['msg_symbol'] + \
                                           " вместо " + self.data['db_symbol'] + "\n"
                return False
        else:
            if self.data['db_symbol'] != self.data['ini_symbol']:
                self.data['commentary'] += "Неверный инструмент!\n" \
                                           " Запущен на " + self.data['msg_symbol'] + \
                                           " вместо " + self.data['db_symbol'] + "\n"
                return False
        return True


    def CheckTimeframe(self):
        if self.data['msg_time'] > self.data['ini_time']:
            if self.data['db_timeframe'] != self.data['msg_timeframe']:
                self.data['commentary'] += "Неверный таймфрейм!\n" \
                                           " Запущен на " + self.data['msg_timeframe'] + \
                                           " вместо " + self.data['db_timeframe'] + "\n"
                return False
        else:
            if self.data['db_timeframe'] != self.data['ini_timeframe']:
                self.data['commentary'] += "Неверный таймфрейм!\n" \
                                           " Запущен на " + self.data['ini_timeframe'] + \
                                           " вместо " + self.data['db_timeframe'] + "\n"
                return False
        return True


    def CheckAccount(self):
        if self.data['msg_time'] > self.data['ini_time']:
            if self.data['db_account'] != self.data['msg_account']:
                self.data['commentary'] += "Неверный аккаунт!\n" \
                                           " Запущен на " + str(self.data['msg_account']) + \
                                           " вместо " + str(self.data['db_account']) + "\n"
                return False
        else:
            if self.data['db_account'] != self.data['ini_account']:
                self.data['commentary'] += "Неверный аккаунт!\n Запущен на " + str(self.data['ini_account']) + \
                                           " вместо " + str(self.data['db_account']) + "\n"
                return False
        return True


    def CheckParams(self):
        # Заполнение поля комментарий
        if self.data['db_params']:
            if self.data['ini_params']:

                db_params_dict = self.ParseParams(self.data['db_params'])
                ini_params_dict = self.ParseParams(self.data['ini_params'])
                difference = self.CmpParams(db_params_dict, ini_params_dict)
                if len(difference) == 0:
                    return True
                else:
                    self.data['commentary'] += difference.lstrip()
                    return False
            else:
                self.data['commentary'] += "В логах отсутствуют параметры!\n"
                return False
        self.data['commentary'] += "В БД отсутствуют параметры!\n"
        return False


    def ParseParams(self, param_str):
        param_tuples = param_str.split('\n')
        param_dict = {}
        for elem in param_tuples:
            # print (elem)
            parts = elem.split('=')
            # print("split into ", str(parts))
            if len(parts) == 2 and len(parts[0]) > 0:
                parts[0] = parts[0].rstrip().lstrip()
                parts[1] = parts[1].rstrip().lstrip()
                if parts[0] == "Expert_RobotID":
                    continue
                try:
                    val = float(parts[1])
                    param_dict[parts[0]] = val
                except ValueError:
                    if parts[1] == "false":
                        param_dict[parts[0]] = 0
                    elif parts[1] == "true":
                        param_dict[parts[0]] = 1
                    else:
                        param_dict[parts[0]] = parts[1]
        return param_dict


    def CmpParams(self, db_params, msg_params):
        result = ""
        for key in db_params.keys():
            if not (key in msg_params):
                result += "Параметр " + key + " отсутствует в логах!\n"
            elif db_params[key] != msg_params[key]:
                result += "Параметр " + key + " имеет значение:\n" + str(msg_params[key]) + " --вместо-- " + str(db_params[key]) + "\n"
                # print(msg_params[key], "____", db_params[key])
                # print("with length ",len(msg_params[key]), len(db_params[key]))
                # print("with type ", type(msg_params[key]), type(db_params[key]))
        for key in msg_params.keys():
            if not (key in db_params):
                result += "Параметр " + key + " отсутствует в БД!\n"

        return result


    def CheckPermissions(self):
        result = True
        perm = self.data['msg_trading_enabled'] if self.data['msg_time'] > self.data['ini_time'] else self.data['ini_trading_enabled']
        if perm % 2 != 1:
            self.data['is_demo'] = True
        perm //= 2
        if perm % 2 != 1:
            self.data['commentary'] += "Запрещена автоторговля для робота!\n"
            result = False
        perm //= 2
        if perm % 2 != 1:
            self.data['commentary'] += "Запрещена автоторговля для робота на счёте!\n"
            result = False
        perm //= 2
        if perm % 2 != 1:
            self.data['commentary'] += "Запрещена торговля для счёта!\n"
            result = False
        return result


    def CheckDemo(self):
        return (self.data['msg_trading_enabled'] % 2 == 0)


    def CheckExpiration(self):
        if self.data['symbol_end'] - datetime.timedelta(days=5) <= datetime.date.today():
            self.data['commentary'] += "Истекает срок действия контракта!\n"
            return False
        return True


    def CheckVersion(self):
        if self.data['ini_version'] != self.data['robot_version']:
            self.data['commentary'] += "Неверная версия робота!\n" \
                                       "Запущен на " + self.data['ini_version'] + \
                                       " --вместо-- " + self.data['robot_version'] + "\n"
            return False
        return True
