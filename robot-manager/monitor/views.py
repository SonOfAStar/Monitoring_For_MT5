from django.shortcuts import render

from .monitor_table_class import MonitorTable


def main_view(request):

    table = MonitorTable()

    return render(request, 'robots/monitoring_table.html', {
        'monitoring': True,
        'manager': 'robot',
        'title': 'Main page',
        'display_rows': table(request),
    })
