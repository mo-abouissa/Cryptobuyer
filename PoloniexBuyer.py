from coinmarketcap import Market
import PoloniexWrapper
import json
import pandas as pd

from keys import APIKey, Secret

class poloniexBuyer:

    def definition():
        global amtOfPairs, amtToTrade
        amtOfPairs = 20
        amtToTrade = .50

    # Upon running buyer, initialize new Poloniex instance
    def __init__(self):
        self.poloniexInstance = PoloniexWrapper.poloniex(APIKey, Secret)


    # Retrieve top N currencies by market cap from coinmarketcap
    def retrieveWeeklyOptions(self):

        newMarketSession = Market()
        coins = newMarketSession.ticker(limit=100)

        coinsJSON = json.dumps(coins)
        coinsFormatted = pd.read_json(coinsJSON)

        return coinsFormatted.sort_values(by=["market_cap_usd"], ascending=[False])

    # Retrieve current price of BTC
    def currBTCValue(self):

        Buyer = poloniexBuyer()
        weeklyOptions = Buyer.retrieveWeeklyOptions()

        symbols = weeklyOptions["symbol"].tolist()
        btc = weeklyOptions[(weeklyOptions["symbol"] == "BTC")]
        btcPrice = btc["price_usd"]
        btcAmt = amtToTrade / btcPrice.iloc[0]

        return btcAmt

    #Retrieve top N currencies that are traded on Poloniex
    def retrieveTopNPoloniex(self):

        Buyer = poloniexBuyer()
        weeklyOptions = Buyer.retrieveWeeklyOptions()

        symbols = weeklyOptions["symbol"].tolist()

        # Create list of top N currencies without Bitcoin, then append "BTC_" to them so Poloniex can parse it
        symbolsWithoutBTC = []
        for symbol in symbols[1:]:
            symbolsWithoutBTC.append(symbol)
        symbolsWithoutBTCPrefixed = ["BTC_" + symbol for symbol in symbolsWithoutBTC]

        # Find all currencies that can be traded with BTC
        poloniexPairs = pd.read_json(json.dumps(self.poloniexInstance.returnTicker()))

        # Find the top N pairs by market cap on Poloniex
        topNPoloniexPairs = []
        for symbol in symbolsWithoutBTCPrefixed:
            topNPoloniexPairs.append([col for col in poloniexPairs.columns if symbol in col])
        topNPoloniexPairs = [x for x in topNPoloniexPairs if x != []]
        topNPoloniexPairs = [x for sublist in topNPoloniexPairs for x in sublist]

        # Create new Dataframe of the top N pairs
        frames = []
        for pair in topNPoloniexPairs:
            data = poloniexPairs.filter(like=pair)
            frames.append(data)
            finalPoloniexPairs = pd.concat(frames, axis=1).ix[:,:amtOfPairs]

        return finalPoloniexPairs

    def placeOrders(self):

        # Calculate max BTC order will cost
        Buyer = poloniexBuyer()
        btcAmt = Buyer.currBTCValue()
        maxTotalOrderAmt = btcAmt * amtOfPairs

        # Find the current BTC balance of the account
        currBalance = self.poloniexInstance.returnBalances()
        currBalance = float(currBalance["BTC"])

        # Generate list of orders
        currencies = Buyer.retrieveTopNPoloniex()

        if currBalance < maxTotalOrderAmt:
            return "Sorry, insufficient BTC in your account."
        else:
            for currency in currencies:
                self.poloniexInstance.buy(str(pair), result[currency].ix[7], (btcAmt / currencies[currency].ix[7]))

    if __name__ == '__main__':
        definition()

test = poloniexBuyer()
print test.retrieveTopNPoloniex()

history = json.dumps(test.poloniexInstance.returnTradeHistory("BTC_ETH"))
history = pd.read_json(history)
print history
