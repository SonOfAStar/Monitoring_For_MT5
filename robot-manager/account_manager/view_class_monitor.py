import datetime
import logging
import locale
import copy
from django.utils import timezone

from req_reciever.models import Account, TradeAccountStateWithPositions, TradeAccountStateHistory
from django.db.models import Max

logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


ACCOUNT_DATA_TEMPLATE = {
    'message': None,
    'state': None,
    'account': None,
}


class AccountMonitor:
    def __init__(self):
        self.table = list()
        self.accounts = Account.objects.all().order_by('type')

        self.last_week_end = self.get_friday()
        self.data = {}

        # print("accounted_states", account_states_ids_query)
        # print("self.account_states_with_positions", account_states_with_positions)

    def __call__(self):
        self.calculate()

        self.table = sorted(self.table, key=lambda k: ('status_int' not in k, k.get('status_int', None)))

        return self.table

    def calculate(self):
        account_states_ids_query = TradeAccountStateHistory.objects.filter(timestamp__lte=self.last_week_end.timestamp())
        account_states_ids_query = account_states_ids_query.values('account').annotate(Max('id'))
        account_states_ids = []
        for elem in account_states_ids_query:
            account_states_ids.append(elem['id__max'])
        account_states = TradeAccountStateHistory.objects.filter(id__in=account_states_ids).order_by('account')

        account_states_with_positions = TradeAccountStateWithPositions.objects.values('account')
        account_states_with_positions = account_states_with_positions.annotate(Max('id'))
        account_states_with_positions_ids = []
        for elem in account_states_with_positions:
            account_states_with_positions_ids.append(elem['id__max'])
        account_msgs = TradeAccountStateWithPositions.objects.filter(id__in=account_states_with_positions_ids)
        account_msgs = account_msgs.order_by('account')

        for account in self.accounts:
            self.data[account.id] = copy.deepcopy(ACCOUNT_DATA_TEMPLATE)
            self.data[account.id]['account'] = account
        for msg in account_msgs:
            self.data[msg.account_id]['message'] = copy.deepcopy(msg)
        for state in account_states:
            self.data[state.account_id]['state'] = copy.deepcopy(state)

        for account in self.accounts:
            self.table.append(self.calculate_row(account))

    def calculate_row(self, account):
        data = self.data[account.id]
        row = dict()

        row['type'] = data['account'].type
        row['owner'] = data['account'].owner
        row['number'] = data['account'].name
        row['responsible'] = data['account'].responsible
        row['max_risk'] = data['account'].max_risk
        row['sum_risk'] = float(data['message'].sum_risk) if data['message'] is not None else -1.0
        row['balance'] = float(data['message'].balance) if data['message'] is not None else -1.0
        reported_balance = float(data['state'].balance) if data['state'] is not None else -1.0
        row['reported_balance_deal'] = data['state'].deals_ticket if data['state'] is not None else 0
        row['balance_change'] = row['balance'] - reported_balance
        row['balance_change_prcnt'] = row['balance_change'] / reported_balance * 100
        row['last_update'] = datetime.datetime.fromtimestamp(data['message'].timestamp) if data['message'] is not None \
            else datetime.datetime(year=1970, month=1, day=1, hour=0, minute=0, second=0)
        row['deals'] = self.parse_deals(account)
        # print(row['deals'])
        status_n_comment = self.calculate_status(row)
        row['status'] = status_n_comment['status']
        row['status_int'] = status_n_comment['status_int']
        row['commentary'] = status_n_comment['commentary']
        row['sum_risk_percent'] = status_n_comment['risk_percent']

        # preparing string representations for better visual experience
        row['balance_str'] = locale.format_string('%.2f', row['balance'], grouping=True)
        row['balance_change_str'] = locale.format_string('%.2f', row['balance_change'], grouping=True)
        row['balance_change_prcnt_str'] = locale.format_string("%.2f", row['balance_change_prcnt'], grouping=True)
        row['sum_risk_str'] = locale.format_string('%.2f', row['sum_risk'], grouping=True)
        row['sum_risk_percent_str'] = locale.format_string('%.2f', row['sum_risk_percent'], grouping=True)

        row['last_update_str'] = '{0:%Y-%m-%d %H:%M}'.format(row['last_update'])

        row['commentary_snapshot'] = row['commentary'].split("\n")[0]
        if len(row['commentary']) > len(row['commentary_snapshot']) + 1:
            row['commentary_snapshot'] += "..."

        # print(row)
        return row

    def parse_deals(self, account):
        if self.data[account.id]['message'] is None or len(self.data[account.id]['message'].positions) == 0:
            return []

        positions = list()
        positions_strs = self.data[account.id]['message'].positions
        # print('Positions: ', positions_strs)
        position_params_str = positions_strs.split('\n')

        for position_param in position_params_str:
            # print('Position:', position_param)
            if len(position_param) == 0:
                break
            position = PositionInfo(position_param)
            positions.append(position.to_dict())
        return positions

    @staticmethod
    def calculate_status(row):
        err = False
        warn = False
        result = {
            'status': '',
            'status_int': 1,
            'commentary': '',
            'risk_percent': 0.0
        }

        projected_msg_time = datetime.datetime.now() - datetime.timedelta(minutes=6)
        projected_msg_time = timezone.make_aware(projected_msg_time)
        # projected_msg_time = projected_msg_time)
        if row['last_update'].tzinfo is None or row['last_update'].tzinfo.utcoffset(row['last_update']) is None:
            row['last_update'] = timezone.make_aware(row['last_update'])
        # print(projected_msg_time, " <--to--> ", row['last_update'])
        # print(projected_msg_time > row['last_update'])
        if projected_msg_time > row['last_update']:
            err = True
            result['commentary'] += "Истекло время ожидания сообщения!\n"

        risk_percent = row['sum_risk']/row['balance'] * 100
        result['risk_percent'] = risk_percent

        for deal in row['deals']:
            if deal['sl'] == 0.0:
                err = True
                result['commentary'] += "На символе {} отсутствует стоп-лосс!\n".format(deal['symbol'])

        if risk_percent > row['max_risk']:
            warn = True
            result['commentary'] += "Превышен риск на счёте!\n"

        if err:
            result['status'] = "ERR"
            result['status_int'] = 1
        elif warn:
            result['status'] = "WARN"
            result['status_int'] = 2
        else:
            result['status'] = "OK"
            result['status_int'] = 3

        return result

    @staticmethod
    def get_friday():
        today = datetime.date.today()
        day = today.weekday()
        day_delta = datetime.timedelta(days=day + 3)
        friday = today - day_delta
        t = datetime.time(hour=19, minute=0)
        friday = datetime.datetime.combine(friday, t)
        friday = timezone.make_aware(friday)

        return friday


class PositionInfo:
    def __init__(self, string_repr):
        self.price = 0.0
        self.price_str = '0.00'
        self.volume = 0.0
        self.volume_str = '0.00'
        self.sl = 0.0
        self.sl_str = '0.00'
        self.id = 0
        self.id_str = '0'
        self.magic = 0
        self.magic_str = '0'
        self.symbol = "empty"
        self.risk = 0.0
        self.risk_str = '0.00'
        self.result = 0

        params = string_repr.split(',')
        for param in params:
            if len(param) == 0:
                continue

            details = param.split(':')
            if len(details) != 2:
                break
            if details[0] == 'price':
                self.price = float(details[1])
                self.price_str = locale.format_string('%.2f', self.price, grouping=True)
                self.result += 1
            if details[0] == 'volume':
                self.volume = float(details[1])
                self.volume_str = locale.format_string('%.2f', self.volume, grouping=True)
                self.result += 1
            if details[0] == 'sl':
                self.sl = float(details[1])
                self.sl_str = locale.format_string('%.2f', self.sl, grouping=True)
                self.result += 1
            if details[0] == 'id':
                self.id = int(details[1])
                self.id_str = locale.format_string('  %d  ', self.id, grouping=True)
                self.result += 1
            if details[0] == 'magic':
                self.magic = int(details[1])
                self.magic_str = locale.format_string('  %d  ', self.magic, grouping=True)
                self.result += 1
            if details[0] == 'risk':
                self.risk = float(details[1])
                self.risk_str = locale.format_string('%.2f', self.risk, grouping=True)
                self.result += 1
            if details[0] == 'symbol':
                self.symbol = details[1]
                self.result += 1

    def __str__(self):
        res_str = 'Позиция по символу {}, Цена открытия {}, ID {}'.format(self.symbol, self.price_str, self.id)
        return res_str

    def to_dict(self):
        result = {
            'price': self.price,
            'price_str': self.price_str,
            'volume': self.volume,
            'volume_str': self.volume_str,
            'sl': self.sl,
            'sl_str': self.sl_str,
            'self': self.id,
            'id_str': self.id_str,
            'magic': self.magic,
            'magic_str': self.magic_str,
            'symbol': self.symbol,
            'risk': self.risk,
            'risk_str': self.risk_str,
            'result': self.result,
        }
        return result
