from datetime import datetime  # Работаем с датой и временем
import backtrader as bt
import providers.finam as finam
from BT.Systems.base import StrategyBase
from BT.Systems.base import BClr


class MACrossOver(StrategyBase):
    # Moving average parameters
    params = (
        ('IsOptimizing', False),  # Стратегия оптимизируется в данный момент ?
        ('pfast', 20),
        ('pslow', 50),
    )

    def __init__(self):
        StrategyBase.__init__(self)
        self.dataclose = self.datas[0].close
        # Instantiate moving averages
        self.slow_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.pslow)
        self.fast_sma = bt.indicators.MovingAverageSimple(self.datas[0], period=self.params.pfast)

    def next(self):
        # self.log(f'Close={self.dataclose[0]:8.2f}')


        # Check if we are in the market
        if not self.position:
            # We are not in the market, look for a signal to OPEN trades

            # If the 20 SMA is above the 50 SMA
            if self.fast_sma[0] > self.slow_sma[0] and self.fast_sma[-1] < self.slow_sma[-1]:
                self.log(f'{BClr.GREEN("LONG position")} {self.dataclose[0]:2f}')
                # Keep track of the created order to avoid a 2nd order
                self.Order = self.buy()
            # Otherwise if the 20 SMA is below the 50 SMA
            elif self.fast_sma[0] < self.slow_sma[0] and self.fast_sma[-1] > self.slow_sma[-1]:
                self.log(f'{BClr.RED("SHORT position")} {self.dataclose[0]:2f}')
                # Keep track of the created order to avoid a 2nd order
                self.Order = self.sell()
        else:
            # We are already in the market, look for a signal to CLOSE trades
            if len(self) >= (self.BarExecuted + 5):
                self.log(f'CLOSE position {self.dataclose[0]:2f}')
                self.Order = self.close()


if __name__ == '__main__':  # Точка входа при запуске этого скрипта

    from_date = datetime(2020, 1, 1)
    to_date = datetime(2020, 12, 31)

    data = finam.to_backtrader_data('SPFB.SBRF', 'hour', from_date, to_date) #, path_save='D:\Py-Prj\Backtrader\BackTrader - Quick Start\ticker_data')
    # Instantiate Cerebro engine
    engine = bt.Cerebro()
    # Add strategy to Engine
    engine.addstrategy(MACrossOver, IsOptimizing=False)
    engine.adddata(data)
    engine.broker.setcash(1000000.0)  # Стартовый капитал для "бумажной" торговли
    start_portfolio_value = engine.broker.getvalue()
    print(f'Starting Portfolio Value: {start_portfolio_value:2f}')
    # Run Engine
    engine.run()
    end_portfolio_value = engine.broker.getvalue()
    print(f'Final Portfolio Value: {end_portfolio_value:2f}')
    pnl = end_portfolio_value - start_portfolio_value
    print(f'PnL: {pnl:.2f}')
    engine.plot()  # Рисуем график. Требуется matplotlib версия 3.2.2 (pip install matplotlib==3.2.2)

