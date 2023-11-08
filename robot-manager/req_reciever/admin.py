import copy
from django.contrib import admin
from .models import RobotInitLog, RobotLog, Robot, Setting, RobotFile, RobotCluster
from .models import StockMarket, Broker, Timeframe, Account, Symbol, SymbolSplice

from .models import TradeDeal, TradeAccountStateHistory, TradeAccountStateWithPositions
# from .models import RobotsAdmin, SettingsAdmin
from .models import WeirdLog

# Create custom actions


def my_copy(modeladmin, request, queryset):
    for elem in queryset.all():
        new_elem = elem
        new_elem.id = None
        new_elem.save()


my_copy.short_description = "Copy selected"


def set_to_archive(modeladmin, request, queryset):
    queryset.update(archive=True)


set_to_archive.short_description = "Send selected to archive"
set_to_archive.allowed_permissions = ('change',)


# Create your models here.


class SettingsAdmin(admin.ModelAdmin):

    list_display = ('name', 'symbol', 'timeframe')
    list_display_links = ('name', 'symbol', 'timeframe')
    list_filter = ('symbol_id', 'timeframe_id')
    actions = ['my_copy']

    def symbol(self, obj):
        return Symbol.objects.get(pk=obj.symbol_id)

    def timeframe(self, obj):
        return Timeframe.objects.get(pk=obj.timeframe_id)

    def my_copy(modeladmin, request, queryset):
        for elem in queryset.all():
            new_elem = elem
            new_elem.id = None
            new_elem.name = "Copy - " + elem.name
            new_elem.save()
    my_copy.short_description = "Создать копию выбранных элементов"


class RobotsAdmin(admin.ModelAdmin):

    list_display = ('name', 'robot_cluster', 'account', 'owner', 'symbol', 'timeframe', 'active', 'archive')
    list_display_links = ('name', 'robot_cluster', 'account', 'owner', 'symbol', 'timeframe')
    list_filter = ('robot_cluster_id', 'account_id', 'active', 'archive')

    def robot_cluster(self, obj):
        return RobotCluster.objects.get(pk=obj.robot_cluster_id)

    def account(self, obj):
        return Account.objects.get(pk=obj.account_id)

    def owner(self, obj):
        return Account.objects.get(pk=obj.account_id).owner

    def symbol(self, obj):
        symbol_id = Setting.objects.get(pk=obj.settings_id).symbol_id
        return Symbol.objects.get(pk=symbol_id)

    def timeframe(self, obj):
        timeframe_id = Setting.objects.get(pk=obj.settings_id).timeframe_id
        return Timeframe.objects.get(pk=timeframe_id)

    actions = ['my_copy', 'set_to_archive']

    def my_copy(self, request, queryset):
        for elem in queryset.all():
            new_elem = elem
            new_elem.active = False
            new_elem.archive = False
            new_elem.name = "Copy - " + elem.name
            new_elem.id = None
            new_elem.save()
    my_copy.short_description = "Создать копию выбранных элементов"

    def set_to_archive(self, request, queryset):
        queryset.update(archive=True)
    set_to_archive.short_description = "Отправить выбранные элементы в архив"
    set_to_archive.allowed_permissions = ('change',)


class RobotFilesAdmin(admin.ModelAdmin):
    list_display = ['name', 'version', 'meta']
    actions = ['my_copy']
    
    def my_copy(modeladmin, request, queryset):
        for elem in queryset.all():
            new_elem = elem
            new_elem.id = None
            new_elem.name = "Copy - " + elem.name
            new_elem.save()
    my_copy.short_description = "Создать копию выбранных элементов"
# Register your models here.


admin.site.register(RobotInitLog)
admin.site.register(RobotLog)
# admin.site.register(Robot)
# admin.site.register(RobotFile)
admin.site.register(RobotCluster)
# admin.site.register(Setting)
admin.site.register(StockMarket)
admin.site.register(Broker)
admin.site.register(Timeframe)
admin.site.register(Account)
admin.site.register(Symbol)
admin.site.register(SymbolSplice)
admin.site.register(WeirdLog)
admin.site.register(TradeDeal)
admin.site.register(TradeAccountStateHistory)
admin.site.register(TradeAccountStateWithPositions)


# Register the admin class with the associated model
admin.site.register(Robot, RobotsAdmin)
admin.site.register(RobotFile, RobotFilesAdmin)
admin.site.register(Setting, SettingsAdmin)
