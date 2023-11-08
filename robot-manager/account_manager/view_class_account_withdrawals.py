import datetime
import logging
import copy

from django.utils import timezone

from req_reciever.models import Account, TradeDeal, TradeDealsAccountedFor


logger = logging.getLogger(__name__)
day_template = {
    'day': datetime.date.today(),
    'deals': [],
    'deal_count': 0,
    'meta': {
        'avg': 0,
        'sum': 0
    }
}

deal_template = {
    'ticket': 9,
    'time': datetime.datetime.now(),
    'profit': 1000,
    'meta': {
        'accounted': False,
        'is_extreme': False,
    }
}


class AccounterOfDeals:
    def __init__(self, account_id):
        self.table = {
            'days': [],
            'meta': {'need_attention': False},
        }
        self.deals = None
        self.deals_count = 0
        self.accounted_deals = list()
        self.account = Account.objects.get(pk=account_id)

    def __call__(self):
        self.calculate()
        # print("Got days ", len(self.table['days']))
        return self.table

    def calculate(self):

        db_accounted_deals = TradeDealsAccountedFor.objects.filter(account_id=self.account.id)
        for elem in db_accounted_deals:
            self.accounted_deals.append(elem.ticket)
        print("Accounted deals:", self.accounted_deals)

        db_deals = TradeDeal.objects.filter(account_id=self.account.id).filter(type=2)
        db_deals = db_deals.filter(reason=0).order_by('-time')

        self.deals = db_deals
        self.deals_count = len(self.deals)

        # print("Got deals", self.deals_count)

        for deal in self.deals:
            # print(deal)
            day = datetime.datetime.fromtimestamp(deal.time).date()
            new_day = True
            if len(self.table['days']) > 0:
                if day == self.table['days'][-1]['day']:
                    new_day = False
                    # print("Got old day")

            if new_day:
                temp = copy.deepcopy(day_template)
                self.table['days'].append(temp)
                self.table['days'][-1]['day'] = day

            new_deal = copy.deepcopy(deal_template)
            new_deal['ticket'] = deal.ticket
            new_deal['time'] = datetime.datetime.fromtimestamp(deal.time)
            new_deal['profit'] = deal.profit
            new_deal['meta']['accounted'] = deal.ticket in self.accounted_deals

            self.table['days'][-1]['deals'].append(new_deal)
            self.table['days'][-1]['meta']['sum'] += abs(new_deal['profit'])

        # print("Finished with deals, recalculating ")
        for num in range(0, len(self.table['days'])):
            self.table['days'][num]['meta']['avg'] = self.table['days'][num]['meta']['sum'] / \
                                                     len(self.table['days'][num]['deals'])
            self.table['days'][num]['deal_count'] = len(self.table['days'][num]['deals'])
            # print("In day {} got {} deals".format(
            #     self.table['days'][num]['day'],
            #     self.table['days'][num]['deal_count']
            # ))

            for deal in self.table['days'][num]['deals']:
                if abs(deal['profit']) > self.table['days'][num]['meta']['avg']*2 \
                        or abs(deal['profit']) > 5000:
                    deal['meta']['is_extreme'] = True
                    # print("Got extreme!")
