import datetime
import logging
import copy

from django.utils import timezone

from req_reciever.models import Account, TradeDeal, TradeDealsAccountedFor


logger = logging.getLogger(__name__)


def add_deals(deals, account):
    db_account = Account.objects.get(pk=account)

    db_deals = TradeDeal.objects.filter(ticket__in=deals)
    log_str = "Adding following deals to the accounted list, as containing insertion/extraction of money:\n{}".format(
        db_deals
    )
    logger.debug(msg=log_str)
    TradeDealsAccountedFor.objects.bulk_create(
        TradeDealsAccountedFor(
            account=db_account,
            deal=deal,
            ticket=deal.ticket,
            timestamp=deal.time,
            profit=deal.profit
        ) for deal in db_deals
    )


def delete_deals(deals):

    db_deals = TradeDealsAccountedFor.objects.filter(ticket__in=deals)

    log_str = "Deleting following deals from the accounted list, as containing insertion/extraction of money:\n" \
              "{}".format(db_deals)
    logger.debug(msg=log_str)
    for deal in db_deals:
        deal.delete()
