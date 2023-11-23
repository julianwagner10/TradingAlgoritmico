import backtrader as bt
import datetime as dt
from strategy import TestStrategy

cerebro = bt.Cerebro()
cerebro.broker.setcash(100000)

# Create a Data Feed
data = bt.feeds.YahooFinanceCSVData(
        dataname='data-base-oracle.csv',
        # Do not pass values before this date
        fromdate=dt.datetime(2000, 1, 1),
        # Do not pass values after this date
        todate=dt.datetime(2000, 12, 31),
        reverse=False)

cerebro.adddata(data)
cerebro.addstrategy(TestStrategy)

print('Mi portafolio inicial:  %.2f' % cerebro.broker.getvalue())
cerebro.run()


print('Mi portafolio inicial:  %.2f' % cerebro.broker.getvalue())

cerebro.plot()