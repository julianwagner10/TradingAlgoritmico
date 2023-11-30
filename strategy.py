import os
import sys
import backtrader as bt
import datetime  # For datetime objects
import matplotlib.pyplot as plt

class MACDStrategy(bt.Strategy):
    params = (
        ("macd_short", 12),
        ("macd_long", 26),
        ("macd_signal", 9),
        ('printlog', False),
    )

    def __init__(self):
        # Crear el indicador MACD
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.macd = bt.indicators.MACD(
            self.data.close,
            period_me1=self.params.macd_short,
            period_me2=self.params.macd_long,
            period_signal=self.params.macd_signal
        )

    def log(self, txt, dt=None, doprint=False):
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

        if self.order:
            return

        # Check if we are in the market
        if not self.position:
        
            if self.macd.macd[0] > self.macd.signal[0] and self.macd.macd[-1] <= self.macd.signal[-1]:
                # Señal de compra: MACD cruza de abajo hacia arriba a la señal
                self.log('BUY CREATE MACD, %.2f' % self.dataclose[0],doprint=True)
                self.order = self.buy()

        else:
            if self.macd.macd[0] < self.macd.signal[0] and self.macd.macd[-1] >= self.macd.signal[-1]:
                # Señal de venta: MACD cruza de arriba hacia abajo a la señal
                self.log('SELL CREATE MACD, %.2f' % self.dataclose[0],doprint=True)
                self.order = self.sell()


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

        #self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' %
        #         (trade.pnl, trade.pnlcomm))

    def next(self):
        crossover_value = self.crossover[0]

        if self.order:
            return

        # Check if we are in the market
        if not self.position:        
            if crossover_value == 1:
                self.log('BUY CREATE GOLDEN, %.2f' % self.dataclose[0],doprint=True)
                self.order = self.buy()
        else:
            if crossover_value == -1:
                self.log('SELL CREATE GOLDEN, %.2f' % self.dataclose[0],doprint=True)
                self.order = self.sell()

    def stop(self):
        self.log('Ending Value %.2f' %
                 (self.broker.getvalue()), doprint=True)


class Bolling_Bands_Strategy(bt.Strategy):
    params = (('printlog', False),)

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        self.boll = bt.ind.BollingerBands(period=20, devfactor=2.5)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.dataclose[0])

        # Check if an order is pending ... if yes, we cannot send a 2nd one
        if self.order:
            return

        # Check if we are in the market
        if not self.position:    
        # Estrategia Bollinger Bands
            if (self.dataclose[0] > self.boll.lines.bot and self.dataclose[-1] <= self.boll.lines.bot[-1]):
                self.log('BUY CREATE Bollinger Bands, %.2f' % self.dataclose[0],doprint=True)
                self.order = self.buy()
        else:
            if (self.dataclose[0] < self.boll.lines.top and self.dataclose[-1] >= self.boll.lines.top[-1]):
                self.log('SELL CREATE Bollinger Bands, %.2f' % self.dataclose[0],doprint=True)
                self.order = self.sell()



class RSI_Strategy(bt.Strategy):
    params = (('printlog', False),)

    def log(self, txt, dt=None, doprint=False):
        if self.params.printlog or doprint:
            dt = dt or self.datas[0].datetime.date(0)
            print('%s, %s' % (dt.isoformat(), txt))

    def __init__(self):
        # Keep a reference to the "close" line in the data[0] dataseries
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None
        
        self.rsi = bt.ind.RSI(period=14, safediv=True)

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:
            # Buy/Sell order submitted/accepted to/by broker - Nothing to do
            return

        # Check if an order has been completed
        # Attention: broker could reject order if not enough cash
        if order.status in [order.Completed]:
            if order.isbuy():
                self.log('BUY EXECUTED, %.2f' % order.executed.price)
            elif order.issell():
                self.log('SELL EXECUTED, %.2f' % order.executed.price)

        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')

        # Write down: no pending order
        self.order = None

    def next(self):
        # Simply log the closing price of the series from the reference
        #self.log('Close, %.2f' % self.dataclose[0])

        if self.order:
            return

        # Check if we are in the market
        if not self.position:  

            if self.rsi < 30:
                self.log('BUY CREATE RSI, %.2f' % self.dataclose[0],doprint=True)
                # Keep track of the created order to avoid a 2nd order
                self.order = self.buy()

        else:
            # Already in the market ... we might sell
            if (self.rsi > 70):
                self.log('SELL CREATE RSI, %.2f' % self.dataclose[0],doprint=True)

                # Keep track of the created order to avoid a 2nd order
                self.order = self.sell()


# Configurar el entorno de Backtrader
if __name__ == '__main__':
    modpath = os.path.dirname(os.path.abspath(sys.argv[0]))
    datapath = os.path.join(modpath, r'C:\Users\Mi PC\Desktop\TradingAlgoritmico\orcl-1995-2014.txt')
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
    cerebro.addstrategy(MACDStrategy)
    cerebro.addstrategy(Bolling_Bands_Strategy)
    cerebro.addstrategy(RSI_Strategy)

    cerebro.broker.setcash(10000.0)

    cerebro.addsizer(bt.sizers.FixedSize, stake=10)

    cerebro.broker.setcommission(commission=0.001)

    print('Capital Inicial: %.2f' % cerebro.broker.getvalue())

    cerebro.run(maxcpus=1)

    print('Capital Final: %.2f' % cerebro.broker.getvalue())

    # Graficar la estrategia
    cerebro.plot(style='candlestick')  
    
    # Mostrar el gráfico
    plt.show()