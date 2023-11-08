#######
#######
####### Class, uniting all the log parsing.
#######
#######

import json
import datetime
import logging
from dateutil import parser
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404

from .log_formats import ALL_FORMATS
from .models import Robot, RobotLog, RobotInitLog, WeirdLog
from .models import Account, TradeOrder, TradeDeal
from .models import TradeAccountStateWithPositions, TradeAccountStateHistory


logger = logging.getLogger(__name__)


class DarwintLog:
    def __init__(self, request):
        self.data = {}
        self.log_type = "unknown"
        self.robot_server_ip = "unknown"
        self.request = request

        self.correct = self.unpack()

        if self.correct:
            self.correct = self.check_type()

    def unpack(self):

        self.robot_server_ip = self.get_ip()
        request_string = self.request.body.decode('utf-8', "ignore")

        end = len(request_string)
        if ord(request_string[end - 1]) == 0:
            end -= 1

        try:
            self.data.update(json.loads(request_string[:end]))
        except json.decoder.JSONDecodeError:
            logger.debug("DarwintLog failed recognising django format")
            return False

        return True

    def check_type(self):

        for format_type in ALL_FORMATS.keys():
            log_format = ALL_FORMATS[format_type]
            logger.debug(str(log_format.keys()) + "--" + str(self.data.keys()))
            if set(log_format.keys()) == set(self.data.keys()):
                for key in log_format.keys():
                    if isinstance(self.data[key], type(log_format[key])):
                        continue
                    else:
                        logger.error("Received corrupted " + format_type + " instace. A new attempt necessary.")
                        logger.error("Received corrupted key " + key + " instace. Received type: "
                                     + str(type(self.data[key])) + " required type: " + str(type(log_format[key])))
                        return False
                self.log_type = format_type
                return True

        logger.debug("Received unknown format of log." + str(self.data.keys()))
        return False

    def get_ip(self):
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = self.request.META.get('REMOTE_ADDR')

        return ip

    def to_database(self):
        if not self.correct:
            self.fill_weird_logs()
            return "Incorrect message format."

        if self.log_type == "robot_log" or self.log_type == "robot_sig":

            try:
                robot_info = Robot.objects.get(pk=self.data['robot_id'])
            except ObjectDoesNotExist:
                logger.error("No object with id: " + str(self.data['robot_id']) + "!")
                self.fill_weird_logs()
                return "robot DoesNotExist"

            if self.log_type == "robot_log":
                self.fill_robot_logs(robot_info)

            if self.log_type == "robot_sig":
                self.fill_robot_signals(robot_info)

        elif self.log_type == "account_state" or self.log_type == "account_history":
            try:
                account_info = Account.objects.get(name=self.data['account'])
            except ObjectDoesNotExist:
                logger.error("No object with id: " + str(self.data['account']) + "!")
                self.fill_weird_logs()
                return "Account DoesNotExist"

            if self.log_type == "account_state":
                self.fill_trade_state(account_info)

            if self.log_type == "account_history":
                self.process_history_info(account_info)

        return "Ok"

    def fill_weird_logs(self):
        time = datetime.datetime.now()
        request = self.request
        headers = request.META
        headers_string = ""
        for key in headers.keys():
            headers_string += str(key) + ": " + str(headers[key]) + "\n"

        body = request.body.decode('utf-8')

        log = WeirdLog(
            datetime=time,
            ip=self.robot_server_ip,
            body=body,
            header=headers_string,
        )
        log.save()

    def fill_robot_logs(self, robot_info):
        m_datetime = self.get_time_from_log(self.data['datetime'])

        log = RobotLog(
            datetime=m_datetime,
            robot_volume=self.data['robot_volume'],
            robot=robot_info,
            robot_name=self.data['robot_name'],
            robot_timeframe=self.data['robot_timeframe'],
            robot_symbol=self.data['robot_symbol'],
            robot_trading_enabled=self.data['robot_trading_enabled'],
            robot_limit_orders=self.data['robot_limit_orders'],
            robot_account_code=self.data['robot_account_code'],
            robot_server_ip=self.robot_server_ip,
        )
        log.save()

    def fill_robot_signals(self, robot_info):
        m_datetime = self.get_time_from_log(self.data['datetime'])

        log = RobotInitLog(
            datetime=m_datetime,
            robot=robot_info,
            robot_name=self.data['robot_name'],
            robot_timeframe=self.data['robot_timeframe'],
            robot_symbol=self.data['robot_symbol'],
            robot_params=self.data['robot_params'],
            robot_trading_enabled=self.data['robot_trading_enabled'],
            robot_signal=self.data['robot_signal'],
            robot_account_code=self.data['robot_account_code'],
            robot_version=self.data['robot_version'],
            robot_server_ip=self.robot_server_ip,
        )
        log.save()

    def fill_trade_state(self, account_info):
        position_str = ''
        if len(self.data['positions']) > 1:
            try:
                position_json = json.loads(self.data['positions'])
            except json.decoder.JSONDecodeError:
                logger.debug("DarwintLog failed recognising django format")
                return False
            for position in position_json:
                for key in position.keys():
                    position_str += key + ":" + str(position[key]) + ","
                position_str += "\n"

        log = TradeAccountStateWithPositions(
            account=account_info,
            balance=self.data['balance'],
            timestamp=self.data['timestamp'],
            sum_risk=self.data['sum_risk'],
            positions=position_str,
        )
        log.save()
        pass

    def prepare_history(self, account_info):
        db_orders = TradeOrder.objects.filter(account_id=account_info.id)
        db_deals = TradeDeal.objects.filter(account_id=account_info.id)
        db_account_states = TradeAccountStateHistory.objects.filter(account_id=account_info.id)

        if not self.data['rewrite_history']:
            # orders processing
            orders = self.data['orders']
            order_tickets = []
            for order in orders:
                order_tickets.append(order['ticket'])

            db_orders = db_orders.filter(ticket__in=order_tickets)

            # deals processing
            deals = self.data['deals']
            deal_tickets = []
            for deal in deals:
                deal_tickets.append(deal['ticket'])

            db_deals = db_deals.filter(ticket__in=deal_tickets)

            # history states processing
            db_account_states = db_account_states.filter(deals_ticket__in=deal_tickets)

        logger.debug("Preparing history deals for deletion.")
        logger.debug("Deleting deals:\n"+str(db_deals))
        logger.debug("Deleting orders:\n"+str(db_orders))
        logger.debug("Deleting states:\n"+str(db_account_states))

        db_deals.delete()
        db_orders.delete()
        db_account_states.delete()

    def process_history_info(self, account_info):
        self.prepare_history(account_info)

        # orders processing
        orders = self.data['orders']
        orders_to_save = list()

        for order in orders:
            orders_to_save.append(self.fill_trade_order(account_info, order))

        TradeOrder.objects.bulk_create(orders_to_save)

        # deals processing
        deals = self.data['deals']
        deals_to_save = list()

        for deal in deals:
            deals_to_save.append(self.fill_trade_deal(account_info, deal))

        TradeDeal.objects.bulk_create(deals_to_save)

        # account states processing
        state_history = TradeAccountStateHistory.objects.filter(account_id=account_info.id)
        state_history = state_history.order_by('-timestamp')

        if state_history.exists():
            last_state = state_history[0]
        else:
            logger.debug("Started full recalculation of account states, initialise history with zero.")
            last_state = TradeAccountStateHistory(
                account=account_info,
                timestamp=0,
                balance=0,
                deals_ticket=-1,
            )
            last_state.save()

        last_saved_balance = float(last_state.balance)
        new_balance = last_saved_balance

        states_to_save = list()

        for deal in deals:
            new_balance += deal['profit'] + deal['fee'] + deal['commission'] + deal['swap']

            log_str = "State with {} profit, {} fee, {} commission, {} swap. Now has {}".format(
                float(deal['profit']),
                float(deal['fee']),
                float(deal['commission']),
                float(deal['swap']),
                new_balance
            )
            logger.debug(log_str)
            states_to_save.append(self.fill_account_state_history(account_info, deal, new_balance))
        TradeAccountStateHistory.objects.bulk_create(states_to_save)

    def fill_trade_order(self, account_info, order):
        log = TradeOrder(
            account=account_info,
            ticket=order['ticket'],
            setup_time=order['setup_time'],
            type=order['type'],
            expiration_time=order['expiration_time'],
            done_time=order['done_time'],
            setup_msc_time=order['setup_msc_time'],
            done_msc_time=order['done_msc_time'],
            filling_type=order['filling_type'],
            time_type=order['time_type'],
            magic=order['magic'],
            reason=order['reason'],
            position_id=order['position_id'],
            close_by_position_id=order['close_by_position_id'],
            volume_initial=order['volume_initial'],
            volume_current=order['volume_current'],
            price_open=order['price_open'],
            sl=order['sl'],
            tp=order['tp'],
            price_current=order['price_current'],
            price_stoplimit=order['price_stoplimit'],
            symbol=str(order['symbol']),
            comment=str(order['comment']),
            external_id=str(order['external_id']),
        )
        log_str = "Saving order " + str(log.ticket)
        logger.debug(log_str)
        return log

    def fill_trade_deal(self, account_info, deal):
        log = TradeDeal(
            account=account_info,
            ticket=deal['ticket'],
            order_id=deal['order_id'],
            time=deal['time'],
            time_msc=deal['time_msc'],
            type=deal['type'],
            entry=deal['entry'],
            magic=deal['magic'],
            reason=deal['reason'],
            position_id=deal['position_id'],
            volume=deal['volume'],
            price=deal['price'],
            commission=deal['commission'],
            swap=deal['swap'],
            profit=deal['profit'],
            fee=deal['fee'],
            symbol=str(deal['symbol']),
            comment=str(deal['comment']),
            external_id=str(deal['external_id']),
        )
        log_str = "Saving deal " + str(log.ticket)
        logger.debug(log_str)
        return log

    def fill_account_state_history(self, account_info, deal_json, new_balance):
        new_state = TradeAccountStateHistory(
            account=account_info,
            timestamp=deal_json['time'],
            balance=new_balance,
            deals_ticket=deal_json['ticket'],
        )
        return new_state

    @staticmethod
    def get_time_from_log(str_time):
        time = parser.parse(str_time)
        time += datetime.timedelta(hours=3)
        if timezone.is_naive(time) or time.tzinfo is None or time.tzinfo.utcoffset(time) is None:
            current_tz = timezone.get_current_timezone()
            time = timezone.make_aware(time)
            print("a:", time)
            # time = current_tz.normalize(time.astimezone(current_tz))
            # print("b:", time)
        return time
