import backtrader as bt


def get_ticker_data(datas, symbol):
    for data in datas:
        if symbol in data._dataname:
            return data


def get_ticker_id(datas, symbol):
    count = 0
    for data in datas:
        if symbol in data._dataname:
            return count
        count += 1
