import backtrader as bt  # Библиотека BackTrader (pip install backtrader)
import providers.telegram as telegram


class BClr:
    @staticmethod
    def RED(txt): return f"\033[91m{txt}\033[0m"
    @staticmethod
    def GREEN( txt): return f"\033[92m{txt}\033[0m"
    @staticmethod
    def YELLOW(txt): return f"\033[93m{txt}\033[0m"
    @staticmethod
    def BLUE(txt): return f"\033[94m{txt}\033[0m"
    @staticmethod
    def CYAN(txt): return f"\033[96m{txt}\033[0m"
    @staticmethod
    def HEADER(txt): return f"\033[95m{txt}\033[0m"
    @staticmethod
    def BOLD(txt): return f'\033[1m{txt}\033[0m'
    @staticmethod
    def UNDERLINE(txt): return f'\033[4m{txt}\033[0m'


class StrategyBase(bt.Strategy):

    def log(self, txt, dt=None, to_telegram=False, doprint=False):
        """ Вывод строки с датой в консоль"""
        if self.params.IsOptimizing and not doprint:  # IsOptimizing in process ?
            return

        # dt = dt or self.datas[0].datetime.date(0)  # Заданная дата или дата текущего бара
        # text = f'[{self.__class__.__name__}] {dt.isoformat()}: {txt}'
        dt = bt.num2date(self.datas[0].datetime[0]) if dt is None else bt.num2date(
            dt)  # Заданная дата или дата текущего бара
        text = f'[{self.__class__.__name__}] {dt.strftime("%d.%m.%Y %H:%M")}: {txt}'
        print(text)  # Выводим имя статегии дату и текст
        if to_telegram:
            telegram.send(text)

    def log_error(self, order, txt):
        self.log(f"{order.info['name']}{txt} "
                 f"Status {order.status}: Ref: {order.ref}, Size: {order.size}, "
                 f"Price: {'NA, ' if not order.price else round(order.price, 5)}"
                 f"Available cash: {self.broker.getvalue()}", to_telegram=True)

    def __init__(self):
        """ Инициализация торговой системы"""
        self.start_cash = self.broker.getvalue()
        self.max_position_profit = 0
        self.BarExecuted = 0  # Номер Бара выполнения заявки
        self.Order = None  # Заявка
        self.Trade = None
        self.isLive = False  # Режим реальной торговли
        self.orderCompleted = False
        self.totalProfit = 0  # Общая прибыль с момента запуска ТС

    def notify_data(self, data, status, *args, **kwargs):
        """Изменение статуса приходящих баров"""
        dataStatus = data._getstatusname(status)  # Получаем статус (только при LiveBars=True)
        print(dataStatus)
        self.isLive = dataStatus == 'LIVE'  # Переход в режим реальной торговли

    def notify_order(self, order: bt.Order):
        """Изменение статуса заявки"""
        if not order.alive():  # Не уведомляем когда заявки в статусах: Created, Submitted, Accepted, Partial
            if order.price is None:  # Для рыночных заявок цена не указывается
                self.log(f'Order #{order.ref} - {"Buy" if order.isbuy() else "Sell"} {order.getordername(order.exectype)} {abs(order.size)} {order.data._dataname} - {order.getstatusname()}')
            else:  # Для лимитных/стоп заявок цена указывается
                self.log(f'Order #{order.ref} - {"Buy" if order.isbuy() else "Sell"} {order.getordername(order.exectype)} {abs(order.size)} {order.data._dataname} @ {order.price:.3f} - {order.getstatusname()}')

        if order.status == order.Completed:  # Заявка полностью исполнена
            self.orderCompleted = True  # Заявка исполнена
            self.BarExecuted = len(self)  # Номер бара, на котором была исполнена заявка
        elif order.status in [order.Canceled, order.Expired, order.Margin, order.Rejected]:  # Заявка отменена / снята по времени действия / нет средств / отклонена брокером
            self.orderCompleted = True  # Заявка исполнена
            if order.status in [order.Canceled]:
                self.log_error(order, f"{BClr.RED('Order Canceled')}")
            if order.status in [order.Rejected]:
                self.log_error(order, f"{BClr.YELLOW('WARNING!')}: Order Rejected")
            if order.status in [order.Margin]:
                self.log_error(order, f"{BClr.YELLOW('WARNING!')}: Order Margin")
        else:  # Во всех остальных случаях (Created, Submitted, Accepted, Partial) - Создана / отправлена брокеру / поставлена на биржу / частично исполнена
            self.orderCompleted = False


    def notify_trade(self, trade: bt.Trade):
        """Изменение статуса сделки"""
        if trade.isclosed:  # Если позиция закрыта
            self.totalProfit += trade.pnl
            self.log(f'{BClr.GREEN("Profit") if trade.pnl > 0 else BClr.RED("Loss")}, Trade={trade.pnl:.2f}, Total = {self.totalProfit:.2f}')

    def stop(self):
        """ Окончание запуска торговой системы"""
        self.log(f'Прибыль: {round(self.broker.getvalue() - self.start_cash,2):.2f}, Параметры:{vars(self.params)}', doprint=True)


'''
    def notify_data(self, ticker_data, status, *args, **kwargs):
        """Изменение статуса приходящих баров"""
        dataStatus = ticker_data._getstatusname(status)  # Получаем статус (только при LiveBars=True)
        print(dataStatus)  # Не можем вывести в лог, т.к. первый статус DELAYED получаем до первого бара (и его даты)
        self.isLive = dataStatus == 'LIVE'  # Переход в режим реальной торговли

    def next(self):
        """Получение исторических баров / нового бара / новой заявки"""
        if not self.isLive:  # Если не в режиме реальной торговли
            return  # то выходим, дальше не продолжаем
        # Check for open orders
        if self.Order:
            return
'''
