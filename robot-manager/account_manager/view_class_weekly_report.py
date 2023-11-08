import datetime
import logging
import locale
from django.utils import timezone

from req_reciever.models import Account, TradeDeal, TradeAccountStateHistory, TradeDealsAccountedFor


logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, locale.locale_alias['ru_ru'])


class WeeklyReport:
    def __init__(self, date):
        if date == "":
            date = datetime.date.today()
        else:
            date = datetime.datetime.strptime(date, "%Y-%m-%d").date()

        self.time_end = self.get_friday(date)
        self.current_week_start = (self.time_end - datetime.timedelta(days=7)).timestamp()
        self.four_weeks_start = (self.time_end - datetime.timedelta(days=28)).timestamp()
        self.period_farthest_start = self.time_end

        self.time_end = self.time_end.timestamp()

        self.next_week = date + datetime.timedelta(days=7)
        self.prev_week = date - datetime.timedelta(days=7)
        apply_next_week = self.get_friday(self.next_week) <= \
                          (self.get_friday(datetime.date.today()) + datetime.timedelta(days=7))

        self.meta = {
            'state_sum': 0.0,
            'current_week_profit': 0.0,
            'four_week_profit': 0.0,
            'period_profit': 0.0,
            'week_start': '{0:%Y-%m-%d %H:%M}'.format(datetime.datetime.fromtimestamp(self.current_week_start)),
            'week_end': '{0:%Y-%m-%d %H:%M}'.format(datetime.datetime.fromtimestamp(self.time_end)),
            'next_week': '{0:%Y-%m-%d}'.format(self.next_week),
            'next_week_applied': apply_next_week,
            'prev_week': '{0:%Y-%m-%d}'.format(self.prev_week),
        }

        # print('start {}, 4weeks {}, 1week{}, end{}'.format(
        #     self.period_farthest_start,
        #     self.four_weeks_start,
        #     self.current_week_start,
        #     self.time_end,
        # ))

        self.table = []

        self.accounts = Account.objects.all().order_by('type')

        self.deals = dict()
        self.deals_count = 0

        self.states = dict()
        self.states_count = 0

        self.accounted_deals = dict()
        self.accounted_deals_count = 0

        for account in self.accounts:
            self.deals[account.id] = list()
            self.states[account.id] = list()
            self.accounted_deals[account.id] = list()

    def __call__(self):
        if self.exists_saved():
            self.load_from_file()
        else:
            self.calculate()
            self.save()
        return self.table

    def calculate(self):
        # print("Started calculating!")
        for account in self.accounts:
            self.period_farthest_start = min(account.last_checkout, self.period_farthest_start)

        self.period_farthest_start = self.period_farthest_start.timestamp()

        self.prepare_deals()
        self.prepare_states()
        self.prepare_accounted_deals()

        # print("Started calculating for each account!")
        for account in self.accounts:
            row = self.get_info_on_account(account)
            self.table.append(row)
            self.meta['state_sum'] += float(row['last_account_state'])
            self.meta['current_week_profit'] += float(row['week_profit'])
            self.meta['four_week_profit'] += float(row['four_week_profit'])
            self.meta['period_profit'] += float(row['period_profit'])

        self.meta['state_sum_str'] = locale.format_string('%.2f', self.meta['state_sum'], grouping=True)
        self.meta['current_week_profit_str'] = locale.format_string('%.2f', self.meta['current_week_profit'], grouping=True)
        self.meta['four_week_profit_str'] = locale.format_string('%.2f', self.meta['four_week_profit'], grouping=True)
        self.meta['period_profit_str'] = locale.format_string('%.2f', self.meta['period_profit'], grouping=True)

    def prepare_deals(self):
        db_deals = TradeDeal.objects.filter(time__gte=self.period_farthest_start).filter(time__lt=self.time_end)
        db_deals = db_deals.order_by('time', 'account')
        self.deals_count = len(db_deals)
        # print("Got {} deals total.".format(self.deals_count))

        for counter in range(0, self.deals_count):
            deal = db_deals[counter]
            self.deals[deal.account_id].append(deal)

    def prepare_states(self):
        db_states = TradeAccountStateHistory.objects.filter(timestamp__gte=self.period_farthest_start)\
            .filter(timestamp__lt=self.time_end)
        db_states = db_states.order_by('timestamp', 'account')
        self.states_count = len(db_states)
        # print("Got {} states total.".format(self.states_count))

        for counter in range(0, self.states_count):
            state = db_states[counter]
            self.states[state.account_id].append(state)

    def prepare_accounted_deals(self):
        db_accounted_deals = TradeDealsAccountedFor.objects.filter(timestamp__gte=self.period_farthest_start)
        self.accounted_deals_count = len(db_accounted_deals)

        for counter in range(0, self.accounted_deals_count):
            accounted_deal = db_accounted_deals[counter]
            self.accounted_deals[accounted_deal.account_id].append(accounted_deal.ticket)


    def get_info_on_account(self, account):
        row = dict()

        row['owner'] = account.owner
        row['number'] = account.name
        row['type'] = account.type
        row['responsible'] = account.responsible

        row['period_profit'] = 0
        row['period_profit_percent'] = 0
        row['period_deal_count'] = 0
        row['period_account_state_sum'] = 0

        row['four_week_profit'] = 0
        row['four_week_profit_percent'] = 0
        row['four_week_deal_count'] = 0
        row['four_week_account_state_sum'] = 0

        row['week_profit'] = 0
        row['week_profit_percent'] = 0
        row['week_deal_count'] = 0
        row['week_account_state_sum'] = 0

        row['last_account_state'] = 0

        week_start_position = 0

        for counter in range(0, len(self.deals[account.id])):
            # process each position and account state
            deal = self.deals[account.id][counter]
            if deal.time < account.last_checkout.timestamp():
                continue

            profit = deal.profit + deal.commission + deal.swap + deal.fee
            if deal.ticket in self.accounted_deals[account.id]:
                profit = 0

            if deal.time > account.last_checkout.timestamp():
                row['period_profit'] += profit
                row['period_deal_count'] += 1
                row['period_account_state_sum'] += self.states[account.id][counter].balance

            if deal.time > self.four_weeks_start:
                row['four_week_profit'] += profit
                row['four_week_deal_count'] += 1
                row['four_week_account_state_sum'] += self.states[account.id][counter].balance

            if deal.time > self.current_week_start:
                # print(self.deals[account.id][counter].time, " <---> ", self.current_week_start)
                if week_start_position == 0:
                    week_start_position = counter
                row['week_profit'] += profit
                row['week_deal_count'] += 1
                row['week_account_state_sum'] += self.states[account.id][counter].balance

        row['period_profit_percent'] = 100 * row['period_profit'] / max(1, row['period_account_state_sum'] /
                                                                        max(1, row['period_deal_count']))

        row['four_week_profit_percent'] = 100 * row['four_week_profit'] / max(1, row['four_week_account_state_sum'] /
                                                                              max(1, row['four_week_deal_count']))

        row['week_profit_percent'] = 100 * row['week_profit'] / max(1, row['week_account_state_sum'] /
                                                                    max(1, row['week_deal_count']))

        # calculating yearly profit percent
        days = (self.time_end - account.last_checkout.timestamp()) // 86400
        row['yearly_normalised_profit_percent'] = float(row['period_profit_percent']) / max(days, 1) * 365

        # converting float values to a better representing sting type
        row['week_success'] = 1 if row['week_profit'] > 0 else -1 if row['week_profit'] < 0 else 0
        row['week_profit_str'] = locale.format_string('%.2f', row['week_profit'], grouping=True)
        row['week_profit_percent'] = locale.format_string('%.2f', row['week_profit_percent'], grouping=True)

        row['four_week_success'] = 1 if row['four_week_profit'] > 0 else -1 if row['four_week_profit'] < 0 else 0
        row['four_week_profit_str'] = locale.format_string('%.2f', row['four_week_profit'], grouping=True)
        row['four_week_profit_percent'] = locale.format_string('%.2f', row['four_week_profit_percent'], grouping=True)

        row['period_success'] = 1 if row['period_profit'] > 0 else -1 if row['period_profit'] < 0 else 0
        row['period_profit_str'] = locale.format_string('%.2f', row['period_profit'], grouping=True)
        row['period_profit_percent'] = locale.format_string('%.2f', row['period_profit_percent'], grouping=True)

        if len(self.deals[account.id]) > 0:
            row['last_account_state'] = self.states[account.id][-1].balance
            row['last_account_deal'] = self.states[account.id][-1].deals_ticket

            # print(" Account: {}, start_ticket: {}, start_time: {}, end_ticket: {}, end_time{}".format(
            #     account.name,
            #     self.deals[account.id][week_start_position].ticket,
            #     self.deals[account.id][week_start_position].time,
            #     self.deals[account.id][-1].ticket,
            #     self.deals[account.id][-1].time,
            # ))

        row['yearly_normalised_success'] = 1 if row['yearly_normalised_profit_percent'] > 0 \
            else -1 if row['yearly_normalised_profit_percent'] < 0 else 0
        row['last_account_state_str'] = locale.format_string('%.2f', row['last_account_state'], grouping=True)
        row['yearly_normalised_profit_percent'] = locale.format_string(
            '%.2f', row['yearly_normalised_profit_percent'], grouping=True
        )

        row['period_start'] = '{0:%Y-%m-%d %H:%M}'.format(account.last_checkout)

        return row

    @staticmethod
    def get_friday(date):
        day = date.weekday()
        day_delta = datetime.timedelta(days=day+3)
        friday = date - day_delta
        t = datetime.time(hour=19, minute=0)
        friday = datetime.datetime.combine(friday, t)
        friday = timezone.make_aware(friday)

        return friday

    def current_week_profit(self):
        return self.current_week_profit

    def four_week_profit(self):
        return self.four_week_profit
    
    def period_profit(self):
        return self.period_profit

    def exists_saved(self):
        return False

    def load_from_file(self):
        pass

    def save(self):
        pass
