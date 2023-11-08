import datetime
from django.db import models


class Timeframe(models.Model):
    name = models.CharField(max_length=255)
    minutes = models.IntegerField(default=0)
    meta = models.TextField(blank=True)
    def __str__(self):
        return self.name


class Broker(models.Model):
    name = models.CharField(max_length=255)
    meta = models.TextField(blank=True)
    def __str__(self):
        return self.name


class StockMarket(models.Model):
    name = models.CharField(max_length=255)
    schedule = models.TextField()
    mon = models.BooleanField(default=True)
    tue = models.BooleanField(default=True)
    wed = models.BooleanField(default=True)
    thu = models.BooleanField(default=True)
    fri = models.BooleanField(default=True)
    sat = models.BooleanField(default=False)
    sun = models.BooleanField(default=False)
    def __str__(self):
        return self.name


class RobotCluster(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    meta = models.TextField(blank=True)
    archive = models.BooleanField(default=False)
    def __str__(self):
        return self.name


class RobotFile(models.Model):
    name = models.CharField(max_length=255)
    version = models.CharField(max_length=255)
    robot_cluster = models.ForeignKey(RobotCluster, on_delete=models.CASCADE)
    meta = models.TextField(blank=True)

    def __str__(self):
        return self.name + " v:" + self.version


class SymbolSplice(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    stock_market = models.ForeignKey(StockMarket, on_delete=models.CASCADE,default=1)

    def __str__(self):
        return self.name


class Symbol(models.Model):
    name = models.CharField(max_length=255)
    date_begin = models.DateField()
    date_end = models.DateField()
    symbol_splice = models.ForeignKey(SymbolSplice, on_delete=models.CASCADE)
    meta = models.TextField(blank=True)

    def __str__(self):
        return self.name


class Account(models.Model):
    name = models.IntegerField()
    owner = models.CharField(max_length=255)
    responsible = models.CharField(max_length=255, default='-----')
    type = models.CharField(max_length=255)
    max_risk = models.IntegerField(default=0)
    broker = models.ForeignKey(Broker, on_delete=models.CASCADE)
    stock_market = models.ForeignKey(StockMarket, on_delete=models.CASCADE)
    last_checkout = models.DateTimeField(default=datetime.datetime(year=2021, month=1, day=1, hour=0, minute=0))

    def __str__(self):
        return str(self.name) + "--" + self.owner + "--" + str(self.broker)


class TradeOrder(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    ticket = models.BigIntegerField(default=-1)

    setup_time = models.BigIntegerField(default=0)
    type = models.IntegerField(default=-1)
    state = models.IntegerField(default=-1)
    expiration_time = models.BigIntegerField(default=0)
    done_time = models.BigIntegerField(default=0)
    setup_msc_time = models.BigIntegerField(default=-1)
    done_msc_time = models.BigIntegerField(default=-1)
    filling_type = models.IntegerField(default=-1)
    time_type = models.IntegerField(default=-1)
    magic = models.BigIntegerField(default=-1)
    reason = models.IntegerField(default=-1)
    position_id = models.IntegerField(default=-1)
    close_by_position_id = models.IntegerField(default=-1)

    volume_initial = models.DecimalField(default=0, decimal_places=6, max_digits=16)
    volume_current = models.DecimalField(default=0, decimal_places=6, max_digits=16)
    price_open = models.DecimalField(default=0, decimal_places=6, max_digits=16)
    sl = models.DecimalField(default=0, decimal_places=6, max_digits=16)
    tp = models.DecimalField(default=0, decimal_places=6, max_digits=16)
    price_current = models.DecimalField(default=0, decimal_places=6, max_digits=16)
    price_stoplimit = models.DecimalField(default=0, decimal_places=6, max_digits=16)

    symbol = models.CharField(max_length=63, blank=True)
    comment = models.CharField(max_length=255, blank=True)
    external_id = models.CharField(max_length=255, blank=True)


class TradeDeal(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)

    ticket = models.BigIntegerField(default=-1)
    order_id = models.IntegerField(default=-1)
    time = models.BigIntegerField(default=0)
    time_msc = models.BigIntegerField(default=-1)
    type = models.IntegerField(default=-1)
    entry = models.IntegerField(default=-1)
    magic = models.BigIntegerField(default=-1)
    reason = models.IntegerField(default=-1)
    position_id = models.IntegerField(default=-1)

    volume = models.DecimalField(default=0, decimal_places=6, max_digits=16)
    price = models.DecimalField(default=0, decimal_places=6, max_digits=16)
    commission = models.DecimalField(default=0, decimal_places=6, max_digits=16)
    swap = models.DecimalField(default=0, decimal_places=6, max_digits=16)
    profit = models.DecimalField(default=0, decimal_places=6, max_digits=16)
    fee = models.DecimalField(default=0, decimal_places=6, max_digits=16)

    symbol = models.CharField(max_length=63, blank=True)
    comment = models.CharField(max_length=255, blank=True)
    external_id = models.CharField(max_length=255, blank=True)

    def __str__(self):
        str_ans = "Deal {}:\n".format(self.id)
        str_ans += 'ticket {}, order {}, time {}, type {}, entry {}, magic {}, reason {}, position {}\n' \
                       'volume {}, price {}, commission {}, swap{} ,profit {}, fee {}' \
                       '\n symbol: \'{}\', comment: \'{}\', ext_id: {}'.format(
                            self.ticket,
                            self.order_id,
                            self.time,
                            self.type,
                            self.entry,
                            self.magic,
                            self.reason,
                            self.position_id,
                            self.volume,
                            self.price,
                            self.commission,
                            self.swap,
                            self.profit,
                            self.fee,
                            self.symbol,
                            self.comment,
                            self.external_id,
                            )
        return str_ans


class TradeDealsAccountedFor(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    deal = models.ForeignKey(TradeDeal, on_delete=models.CASCADE)
    ticket = models.BigIntegerField(default=-1)
    timestamp = models.BigIntegerField(default=0)
    profit = models.DecimalField(default=0, decimal_places=6, max_digits=16)


class TradeAccountStateWithPositions(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    balance = models.DecimalField(default=0, decimal_places=6, max_digits=16)
    timestamp = models.BigIntegerField(default=0)
    sum_risk = models.DecimalField(default=0, decimal_places=6, max_digits=16)
    positions = models.TextField(default="None")


class TradeAccountStateHistory(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    timestamp = models.BigIntegerField(default=0)
    balance = models.DecimalField(default=0, decimal_places=6, max_digits=16)
    deals_ticket = models.BigIntegerField(default=-1)


class Setting(models.Model):
    name = models.CharField(max_length=255)
    symbol = models.ForeignKey(Symbol, on_delete=models.CASCADE)
    timeframe = models.ForeignKey(Timeframe, on_delete=models.CASCADE)
    robot_file = models.ForeignKey(RobotFile, on_delete=models.CASCADE)
    template_file = models.TextField()
    template_params = models.TextField()
    meta = models.TextField(blank=True)
    comment = models.CharField(max_length=255, blank=True)
    def __str__(self):
        return self.name


class Robot(models.Model):
    name = models.CharField(max_length=255)
    settings = models.ForeignKey(Setting, on_delete=models.CASCADE)
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    robot_cluster = models.ForeignKey(RobotCluster, on_delete=models.CASCADE)
    active = models.BooleanField(default=False)
    archive = models.BooleanField(default=False)
    comment = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return str(self.id) + " " + self.name


class RobotLog(models.Model):
    datetime = models.DateTimeField()
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE)
    robot_volume = models.DecimalField(default=0, decimal_places=6, max_digits=16)
    robot_limit_orders = models.IntegerField(default=0)
    robot_trading_enabled = models.IntegerField(default=0)
    robot_name = models.CharField(max_length=100)
    robot_timeframe = models.CharField(max_length=4)
    robot_symbol = models.CharField(max_length=30)
    robot_account_code = models.CharField(max_length=30, default="empty_acc")
    robot_server_ip = models.CharField(max_length=30, default="0.0.0.0")

    def __str__(self):
        return str(self.robot_id) + " " + self.robot_name + ":" + str(self.datetime)


class RobotInitLog(models.Model):
    datetime = models.DateTimeField()
    robot = models.ForeignKey(Robot, on_delete=models.CASCADE)
    robot_trading_enabled = models.IntegerField(default=0)
    robot_params = models.TextField()
    robot_name = models.CharField(max_length=100)
    robot_timeframe = models.CharField(max_length=4)
    robot_symbol = models.CharField(max_length=30)
    robot_account_code = models.CharField(max_length=30, default="empty_acc")
    robot_signal = models.CharField(max_length=3, default="-")
    robot_version = models.CharField(max_length=30, default="empty_version")
    robot_server_ip = models.CharField(max_length=30, default="0.0.0.0")

    def __str__(self):
        return str(self.robot_id) + " " + self.robot_name + ":" + str(self.datetime)


class WeirdLog(models.Model):
    datetime = models.DateTimeField()
    ip = models.CharField(max_length=30, default="0.0.0.0")
    body = models.TextField()
    header = models.TextField()

    def __str__(self):
        return str(self.id) + " : " + self.ip + " : " + str(self.datetime)
