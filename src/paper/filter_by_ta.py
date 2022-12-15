# Target rsi
target_rsi = 75

# Filtering based upon technical indicators
def filter_by_ta(stock, hist, macd, vwap, rsi):
    try:
        if macd.iloc[-1]['MACD_12_26_9'] > macd.iloc[-1]['MACDs_12_26_9']:
            try:
                if rsi.iloc[-1] < target_rsi:
                    try:
                        if vwap.iloc[-1] < hist.iloc[-1]['Close']:
                            return True
                        else:
                            return False
                    except:
                        print('error with', stock['Ticker'])
                else:
                    return False
            except:
                print('error with', stock['Ticker'])
        else:
            return False
    except:
        print('error', stock['Ticker'])