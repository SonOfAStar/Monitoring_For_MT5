import datetime
from django.shortcuts import render
from django.http import HttpResponse

from .view_functions_account_deals import add_deals, delete_deals
from .view_class_weekly_report import WeeklyReport
from .view_class_account_withdrawals import AccounterOfDeals
from .view_class_monitor import AccountMonitor

from req_reciever.models import Account


def index(request):
    return HttpResponse("Hello, World!")


def monitor_view(request):
    # return HttpResponse("This is monitoring app")
    account = AccountMonitor()

    return render(request, 'accounts/monitor_table.html', {
        'monitoring': True,
        'manager': 'account',
        'title': 'Main page',
        'account_info_table': account(),
        'my_time': '{0:%Y-%m-%d %H:%M}'.format(datetime.datetime.now()),
    })


def report_view_dated(request, date):
    # return HttpResponse("This is report app")
    rep = WeeklyReport(date)
    return render(request, 'accounts/weekly_report_table.html', {
        'monitoring': False,
        'manager': 'account',
        'account_info_table': rep(),
        'meta': rep.meta,
    })


def report_view(request):
    # return HttpResponse("This is report app")
    rep = WeeklyReport("")
    return render(request, 'accounts/weekly_report_table.html', {
        'monitoring': False,
        'manager': 'account',
        'account_info_table': rep(),
        'meta': rep.meta,
    })


def account_selection_view(request):
    accounts = Account.objects.all()
    return render(request, 'accounts/account_variant_for_accounting.html', {
        'monitoring': False,
        'manager': 'account',
        'accounts': accounts
    })


def accounter_view(request, id):
    accounter = AccounterOfDeals(id)
    return render(request, 'accounts/accounter_of_deals.html', {
        'monitoring': False,
        'manager': 'account',
        'table': accounter(),
        'account': accounter.account,
    })


def account_for_deals(request):
    deal_str = request.POST.get('deals')
    deal_str = deal_str.lstrip('[').rstrip(']')
    deal_str_arr = deal_str.split(',')

    mode = int(request.POST.get('mode'))
    account = int(request.POST.get('account_id'))

    deal_ids = list()

    for i in range(0, len(deal_str_arr)):
        deal_ids.append(int(deal_str_arr[i]))

    print(deal_ids)

    if mode > 0:
        add_deals(deal_ids, account)
    else:
        delete_deals(deal_ids)
    return HttpResponse("")
