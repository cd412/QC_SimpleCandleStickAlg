class SimpleCandleStickAlg(QCAlgorithm):

    def Initialize(self):
        # Parameters
        self.SetStartDate(2019, 1, 1)
        self.SetEndDate(2019, 3, 31)
        self.SetCash(50000)
        self.SetBenchmark("SPY")
        self.trading = False
        
        # Set brokerage information
        #brk = Brokerages.BrokerageName.InteractiveBrokersBrokerage
        #self.SetBrokerageModel(brk, accountType=AccountType.Margin)
        
        # Definre equity
        self.equity = 'AAPL'
        e = self.AddEquity(self.equity, Resolution.Minute, leverage = 4)
        e.MarginModel = PatternDayTradingMarginModel()
        
        # Set Trading Hours = Buys may be made between 9:45AM ET - 3:50PM ET
        self.Schedule.On(self.DateRules.EveryDay(self.equity), self.TimeRules.At(9, 45), Action(self.OpenOfDay))
        # https://www.quantconnect.com/forum/discussion/1037/day-trading-close-all-positions-at-close-of-day/p1
        self.Schedule.On(self.DateRules.EveryDay(self.equity), self.TimeRules.At(15, 44), Action(self.CloseOfDay))
        
        
        # Create indicators
        self.SetWarmUp(100)
        
        ## Identity
        self.dailyPrice = self.Identity(self.equity, Resolution.Daily, Field.Close)
        self.price = self.Identity(self.equity)
        
        ## EMA8
        self.ema8 = self.EMA(self.equity, 8)
        
        ## Doji
        self.doji = self.CandlestickPatterns.Doji(self.equity, Resolution.Minute)
        
    
    def OpenOfDay(self):
        self.trading = True
    
    def CloseOfDay(self):
        self.Liquidate()
        self.trading = False
    
    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
            Arguments:
                data: Slice object keyed by symbol containing the stock data
        '''
        
        if not self.IsWarmingUp and self.trading:
            
            
            buy_sign = self.price > (IndicatorExtensions.Times(self.dailyPrice, 1.01))
            
            if buy_sign and self.Securities[self.equity].Invested == 0:
                self.LimitOrder(self.equity, 100, self.dailyPrice.Current.Value)
                #self.Debug("Limit buy at {}".format(self.dailyPrice.Current.Value))
