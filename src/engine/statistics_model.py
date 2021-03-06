import numpy as np

class StatisticsModel(object):
    '''金融及统计数据模型'''
    def __init__(self, strategy, config):
        '''
        '''
        self._strategy = strategy
        self.logger = strategy.logger
        self._config = config


    def SMA(self, price:np.array, period, weight):
        sma = 0.0
        smas = []

        if period <= 0:
            return np.array(smas)

        if weight > period or weight <= 0:
            return np.array(smas)

        for i, p in enumerate(price):
            if np.isnan(p):
                p = 0.0
            if i == 0:
                sma = p
            else:
                sma = (sma*(period-weight)+p*weight)/period

            smas.append(sma)

        return np.array(smas)

    def ParabolicSAR(self, high:np.array, low:np.array, afstep, aflimit):
        oParClose = None
        oParOpen = None
        oPosition = None
        oTransition = None

        opc_s = []
        opo_s = []
        opos_s = []
        otran_s = []

        hlen = len(high)
        llen = len(low)

        if hlen <=0 or llen <= 0:
            return np.array(opc_s), np.array(opo_s), np.array(opos_s), np.array(otran_s)

        arr = high if hlen < llen else low

        Af = 0
        ParOpen = 0
        Position = 0
        HHValue = 0
        LLValue = 0
        pHHValue = 0
        pLLValue = 0

        for i, a in enumerate(arr):
            if i == 0:
                Position = 1
                oTransition = 1
                Af = afstep
                HHValue = high[i]
                LLValue = low[i]
                oParClose = LLValue
                ParOpen = oParClose + Af * (HHValue - oParClose)
                if ParOpen > LLValue:
                    ParOpen = LLValue
            else:
                oTransition = 0

                pHHValue = HHValue
                pLLValue = LLValue
                HHValue = HHValue if HHValue > high[i] else high[i]
                LLValue = LLValue if LLValue < low[i] else low[i]

                if Position == 1:
                    if low[i] <= ParOpen:
                        Position = -1
                        oTransition = -1
                        oParClose = HHValue
                        pHHValue = HHValue
                        pLLValue = LLValue
                        HHValue = high[i]
                        LLValue = low[i]

                        Af = afstep
                        ParOpen = oParClose + Af * (LLValue - oParClose)

                        if ParOpen < high[i]:
                            ParOpen = high[i]

                        if ParOpen < high[i-1]:
                            ParOpen = high[i-1]

                    else:
                        oParClose = ParOpen
                        if HHValue > pHHValue and Af < aflimit:
                            if Af + afstep > aflimit:
                                Af = aflimit
                            else:
                                Af = Af + afstep

                        ParOpen = oParClose + Af * (HHValue - oParClose)

                        if ParOpen > low[i]:
                            ParOpen = low[i]

                        if ParOpen > low[i-1]:
                            ParOpen = low[i-1]

                else:
                    if high[i] >= ParOpen:
                        Position = 1
                        oTransition = 1

                        oParClose = LLValue
                        pHHValue = HHValue
                        pLLValue = LLValue
                        HHValue = high[i]
                        LLValue = low[i]

                        Af = afstep
                        ParOpen = oParClose + Af * (HHValue - oParClose)

                        if ParOpen > low[i]:
                            ParOpen = low[i]

                        if ParOpen > low[i-1]:
                            ParOpen = low[i-1]

                    else:
                        oParClose = ParOpen

                        if LLValue < pLLValue and Af < aflimit:
                            if Af + afstep > aflimit:
                                Af = aflimit
                            else:
                                Af = Af + afstep

                        ParOpen = oParClose + Af * (LLValue - oParClose)

                        if ParOpen < high[i]:
                            ParOpen = high[i]

                        if ParOpen < high[i-1]:
                            ParOpen = high[i-1]


            oParOpen = ParOpen
            oPosition = Position

            opc_s.append(oParClose)
            opo_s.append(oParOpen)
            opos_s.append(oPosition)
            otran_s.append(oTransition)

        return np.array(opc_s), np.array(opo_s), np.array(opos_s), np.array(otran_s)

    def Pivot(self, Price, Length, LeftStrength, RightStrength, Instance, HiLo):
        '''
        【说明】
            该函数计算指定周期内的数值型序列值的转折点
            当序列值的CurrentBar小于Length时，该函数返回无效值。
        【参数】
            Price:  用于求转折点的值，必须是np数组或者序列变量
            Length: 需要计算的周期数
            LeftStrength：转折点左边需要的Bar数目，必须小于Length
            RightStrength: 转折点右边需要的Bar数目，必须小于Length
            Instance：设置返回哪一个波峰点，1 - 最近的波峰点，2 - 倒数第二个，以此类推
            HiLo 设置求转折的计算类型，1 - 求高点, -1 - 求低点
        【返回值】
            isPivot     是否找到转折点
            PivotPrice  转折点的值
            PivotBar 转折点出现的Bar到当前Bar的回溯周期索引

        【示例】
            Pivot (Close,10,1,1,1,1);计算Close最近10个周期的波峰点。

        '''
        InstanceCntr = 0
        InstanceTest = False
        LengthCntr = RightStrength

        if len(Price) < Length:
            return False, -1.0, -1

        LPrice = Price[::-1]
        LPlen = len(LPrice)

        while LengthCntr < Length and not InstanceTest:
            CandidatePrice = LPrice[LengthCntr]
            PivotTest = True
            StrengthCntr = LengthCntr + 1

            while StrengthCntr < LPlen and PivotTest and (StrengthCntr - LengthCntr <= LeftStrength):
                if ( HiLo == 1 and CandidatePrice < LPrice[StrengthCntr] ) or ( HiLo == -1 and CandidatePrice > LPrice[StrengthCntr]):
                    PivotTest = False
                else:
                    StrengthCntr = StrengthCntr + 1

            StrengthCntr = LengthCntr - 1
            while PivotTest and (LengthCntr - StrengthCntr <= RightStrength):
                if ( HiLo == 1 and CandidatePrice <= LPrice[StrengthCntr] ) or ( HiLo == -1 and CandidatePrice >= LPrice[StrengthCntr]):
                    PivotTest = False
                else:
                    StrengthCntr = StrengthCntr - 1

            if PivotTest:
                InstanceCntr = InstanceCntr + 1

            if InstanceCntr == Instance:
                InstanceTest = True
            else:
                LengthCntr = LengthCntr + 1

        if InstanceTest:
            return True, CandidatePrice, LengthCntr
        else:
            return False, -1.0, -1
            
        



