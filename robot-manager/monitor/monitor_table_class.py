from django.db import connection
from .monitor_row_class import MonitorRow

class MonitorTable:
    def __init__(self, filters={}, sort=None):
        self.sort = sort
        self.filters = filters
        self.display_rows = []
        self.all_rows = []

    def GetUpdates(self):
        cursor = connection.cursor()
        cleanup_query = "DROP TABLE IF EXISTS tmp_logs, tmp_symbols, tmp_settings, tmp_accounts, tmp_robots, tmp_init_logs"
        cursor.execute(cleanup_query)

        # tmp_symbols
        query = "CREATE TEMPORARY TABLE tmp_symbols" \
                " SELECT symbols.id as symbol_id, symbols.name as symbol_name, symbols.date_end as ends," \
                " symbol_splices.name as splice_name" \
                " FROM req_reciever_symbol as symbols" \
                " LEFT JOIN req_reciever_symbolsplice as symbol_splices ON symbols.id=symbol_splices.id  "
        # print(query)
        cursor.execute(query)

        # tmp_settings
        query = "CREATE TEMPORARY TABLE tmp_settings" \
                " SELECT settings.id as settings_id, settings.name as settings_name, settings.template_params as params," \
                " symbols.symbol_name as symbol_name, symbols.ends," \
                " robot_files.name as robot_file_name, robot_files.version as robot_version," \
                " timeframes.name as timeframe, timeframes.minutes as tf_minutes" \
                " FROM req_reciever_setting as settings" \
                " LEFT JOIN tmp_symbols as symbols ON settings.symbol_id=symbols.symbol_id" \
                " LEFT JOIN req_reciever_timeframe as timeframes ON settings.timeframe_id=timeframes.id" \
                " LEFT JOIN req_reciever_robotfile as robot_files ON settings.robot_file_id=robot_files.id  "
        # print(query)
        cursor.execute(query)

        # tmp_accounts
        query = "CREATE TEMPORARY TABLE tmp_accounts" \
                " SELECT accounts.id as account_id, accounts.name as account_name," \
                " accounts.owner as account_owner," \
                " stock_markets.name as stock_market, stock_markets.schedule as market_schedule, stock_markets.mon," \
                " stock_markets.tue, stock_markets.wed, stock_markets.thu, stock_markets.fri, stock_markets.sat," \
                " stock_markets.sun, brokers.name as broker" \
                " FROM req_reciever_account as accounts" \
                " LEFT JOIN req_reciever_stockmarket as stock_markets ON accounts.stock_market_id=stock_markets.id" \
                " LEFT JOIN req_reciever_broker as brokers ON accounts.broker_id=brokers.id  "
        # print(query)
        cursor.execute(query)

        # tmp_robots
        query = "CREATE TEMPORARY TABLE tmp_robots" \
                " SELECT " \
                " robots.id as robots_id, robots.name as name, robots.active as active, robots.archive as archive," \
                " tmp_settings.symbol_name as symbol,tmp_settings.ends as symbol_end, tmp_settings.params as params," \
                " tmp_settings.timeframe as timeframe, tmp_settings.tf_minutes as tf_minutes, tmp_settings.robot_version," \
                " clusters.name as cluster, tmp_accounts.account_name as account," \
                " tmp_accounts.account_owner as owner, tmp_accounts.broker as broker," \
                " tmp_accounts.market_schedule, tmp_accounts.mon, tmp_accounts.tue, tmp_accounts.wed, tmp_accounts.thu," \
                " tmp_accounts.fri, tmp_accounts.sat, tmp_accounts.sun" \
                " FROM req_reciever_robot as robots" \
                " LEFT JOIN tmp_settings ON robots.settings_id=tmp_settings.settings_id" \
                " LEFT JOIN tmp_accounts ON robots.account_id=tmp_accounts.account_id" \
                " LEFT JOIN req_reciever_robotcluster as clusters ON robots.robot_cluster_id=clusters.id   "
        # print(query)
        cursor.execute(query)

        # tmp_logs
        query = "CREATE TEMPORARY TABLE tmp_logs" \
                " SELECT logs.* FROM(" \
                "( SELECT Max(id) AS log_id, robot_id FROM req_reciever_robotlog GROUP By robot_id) as log_w_max" \
                " JOIN req_reciever_robotlog as logs" \
                " ON log_w_max.robot_id = logs.robot_id AND log_w_max.log_id = logs.id)"
        # print(query)
        cursor.execute(query)

        # tmp_init_logs
        query = "CREATE TEMPORARY TABLE tmp_init_logs" \
                " SELECT logs.* FROM(" \
                "( SELECT Max(id) AS log_id, robot_id FROM req_reciever_robotinitlog GROUP By robot_id) as log_w_max" \
                " JOIN req_reciever_robotinitlog as logs" \
                " ON log_w_max.robot_id = logs.robot_id AND log_w_max.log_id = logs.id)"
        # print(query)
        cursor.execute(query)

        # results
        query = " SELECT " \
                " tmp_robots.robots_id as id, tmp_robots.name as db_robot_name," \
                " tmp_robots.active as active, tmp_robots.archive as archive," \
                " tmp_robots.symbol as db_symbol, tmp_robots.symbol_end," \
                " tmp_robots.params as db_params, tmp_robots.timeframe as db_timeframe," \
                " tmp_robots.tf_minutes as tf_minutes, tmp_robots.cluster, tmp_robots.robot_version," \
                " tmp_robots.account, tmp_robots.owner, tmp_robots.broker," \
                " tmp_robots.market_schedule, tmp_robots.mon, tmp_robots.tue, tmp_robots.wed, tmp_robots.thu," \
                " tmp_robots.fri, tmp_robots.sat, tmp_robots.sun," \
                " tmp_init_logs.robot_account_code as ini_account, tmp_init_logs.robot_params as ini_params," \
                " tmp_init_logs.robot_version as ini_version," \
                " tmp_init_logs.robot_trading_enabled as ini_trading_enabled," \
                " tmp_init_logs.datetime as ini_time, tmp_init_logs.robot_signal as ini_signal," \
                " tmp_init_logs.robot_symbol as ini_symbol, tmp_init_logs.robot_timeframe as ini_timeframe," \
                " tmp_logs.robot_trading_enabled as msg_trading_enabled, tmp_logs.robot_limit_orders as limit_orders," \
                " tmp_logs.robot_volume as volume, tmp_logs.datetime as msg_time," \
                " tmp_logs.robot_symbol as msg_symbol, tmp_logs.robot_timeframe as msg_timeframe," \
                " tmp_logs.robot_account_code as msg_account" \
                " FROM" \
                " tmp_robots" \
                " LEFT JOIN tmp_logs ON tmp_logs.robot_id=tmp_robots.robots_id" \
                " LEFT JOIN tmp_init_logs ON tmp_init_logs.robot_id=tmp_robots.robots_id" \

        # print(query)
        cursor.execute(query)

        return cursor.fetchall()
    # получаемая последовательность столбцов
    # | id | db_robot_name | active | archive
    # | db_symbol | symbol_end | db_params | db_timeframe | tf_minutes
    # | cluster | robot_version | account | owner | broker
    # | market_schedule | mon | tue | wed | thu | fri | sat | sun
    # | ini_account | ini_params | ini_version | ini_trading_enabled
    # | ini_time | ini_signal | ini_symbol | ini_timeframe
    # | msg_trading_enabled | limit_orders | volume | msg_time | msg_symbol | msg_timeframe | msg_account |

    def FillAllRows(self, addr):
        print(addr)
        db_data = self.GetUpdates()
        for elem in db_data:
            new_row = MonitorRow(elem)
            self.all_rows.append(new_row)

    def  FilterAllRows(self):
        new_rows = []
        for row in self.all_rows:
            if row['archive'] and (row['status'] == 'OFF'):
                continue
            new_rows.append(row)
        self.display_rows = new_rows

    def SortDisplayRows(self):
        self.display_rows.sort()

    def __call__(self, request=None):
        addr = request.get_host() if not request is None else "empty"
        self.FillAllRows(addr)
        self.FilterAllRows()
        self.SortDisplayRows()
        return self.display_rows
