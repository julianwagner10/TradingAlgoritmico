import os
import sys
import backtrader as bt
import datetime  # For datetime objects



class GoldenDeathCrossStrategy(bt.Strategy):
    params = (
        ("short_period", 50),
        ("long_period", 200),
        ('printlog', False),
    )

    def __init__(self):
        
        self.dataclose = self.datas[0].close

        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        self.short_ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.short_period)
        self.long_ma = bt.indicators.SimpleMovingAverage(self.datas[0], period=self.params.long_period)
        self.crossover = bt.indicators.CrossOver(self.short_ma, self.long_ma)

    def log(self, txt, dt=None, doprint=False):
        ''' Logging function fot this strategy'''
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            return

        if order.status in [order.Completed]:
            if order.isbuy():
                self.log(
                    'BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                    (order.executed.price,
                     order.executed.value,
                     order.executed.comm))
            else:  # Sell
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm %.2f' %
                         (order.executed.price,
                          order.executed.value,
                          order.executed.comm))
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        self.order = None

    def notify_trade(self, trade):
        if not trade.isclosed:
            return

        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
                 (trade.pnl, trade.pnlcomm))

    def next(self):
        crossover_value = self.crossover[0]
        if crossover_value == 1:
            print('Compre')
            self.order = self.buy()
        elif crossover_value == -1:
            print('Vendi')
            self.order = self.sell()

    def stop(self):
        self.log('Ending Value %.2f' %
                 (self.broker.getvalue()), doprint=True)



# Configurar el entorno de Backtrader
if __name__ == '__main__':
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, r'C:\Users\julia\OneDrive\Desktop\Trading Algoritmico\orcl-1995-2014.txt')

    # Configurar el cerebro de Backtrader
    cerebro = bt.Cerebro()

    # Añadir el data feed
    data = bt.feeds.YahooFinanceCSVData(
        dataname=datapath,
        # Do not pass values before this date
        fromdate=datetime.datetime(1996, 1, 1),
        # Do not pass values before this date
        todate=datetime.datetime(2005, 12, 31),
        # Do not pass values after this date
        reverse=False)
    
    cerebro.adddata(data)

    cerebro.addstrategy(GoldenDeathCrossStrategy)

    cerebro.broker.setcash(10000.0)

    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    cerebro.broker.setcommission(commission=0.001)

    print('Capital Inicial: %.2f' % cerebro.broker.getvalue())

    cerebro.run(maxcpus=1)

    print('Capital Final: %.2f' % cerebro.broker.getvalue())