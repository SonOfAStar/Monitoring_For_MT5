#######
#######
####### Collection of all correct formats of logs for DarwintManager
#######
#######


ROBOT_LOG_FORMAT = {
    'datetime': "datetime.datetime.now(),",
    'robot_id': 1,
    'robot_volume': 0.1,
    'robot_trading_enabled': 15,
    'robot_limit_orders': 0,
    'robot_name': 'name',
    'robot_timeframe': 'MX',
    'robot_symbol': 'TTS-12',
    'robot_account_code': 1112233,
}

ROBOT_SIG_FORMAT = {
    'datetime': "datetime.datetime.now(),",
    'robot_id': 1,
    'robot_signal': 'off',
    'robot_name': 'name',
    'robot_timeframe': 'MX',
    'robot_symbol': 'TTS-12',
    'robot_params': '{"json_str": "val"}',
    'robot_trading_enabled': 15,
    'robot_account_code': 1112233,
    'robot_version': '2.02',
}

ACCOUNT_HISTORY_LOG_FORMAT = {
    'account': 12345,
    'timestamp': 12345,
    'rewrite_history': 0,
    'orders': [],
    'deals': [],
}

ACCOUNT_STATE_LOG_FORMAT = {
    'account': 12345,
    'balance': 12345.6,
    'timestamp': 12345,
    'sum_risk': 12345.6,
    'positions': "json or None",
}

ALL_FORMATS = {
    "robot_log": ROBOT_LOG_FORMAT,
    "robot_sig": ROBOT_SIG_FORMAT,
    "account_state": ACCOUNT_STATE_LOG_FORMAT,
    "account_history": ACCOUNT_HISTORY_LOG_FORMAT,
}
