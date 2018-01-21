# -*- coding: utf-8 -*-

from bot.command import *
import json
import gevent
from gevent.threadpool import ThreadPool
from gevent import monkey; monkey.patch_thread()
import time
import operator
import websocket
from util.webclient import WebClient

class CoinAnalyzer(object):
    def __init__(self):
        self._ws = None
        self._host = 'wss://crix-websocket.upbit.com/sockjs/713/vcjo1nf3/websocket'
        self._data = [{
            'ticket': 'ram macbook'
        }, {
            'type': 'recentCrix',
            'codes': [
                'CRIX.UPBIT.KRW-BTC',
                'CRIX.UPBIT.KRW-DASH',
                'CRIX.UPBIT.KRW-ETH',
                'CRIX.UPBIT.KRW-NEO',
                'CRIX.UPBIT.KRW-BCC',
                'CRIX.UPBIT.KRW-MTL',
                'CRIX.UPBIT.KRW-LTC',
                'CRIX.UPBIT.KRW-STRAT',
                'CRIX.UPBIT.KRW-XRP',
                'CRIX.UPBIT.KRW-ETC',
                'CRIX.UPBIT.KRW-OMG',
                'CRIX.UPBIT.KRW-SNT',
                'CRIX.UPBIT.KRW-WAVES',
                'CRIX.UPBIT.KRW-PIVX',
                'CRIX.UPBIT.KRW-XEM',
                'CRIX.UPBIT.KRW-ZEC',
                'CRIX.UPBIT.KRW-XMR',
                'CRIX.UPBIT.KRW-QTUM',
                'CRIX.UPBIT.KRW-LSK',
                'CRIX.UPBIT.KRW-STEEM',
                'CRIX.UPBIT.KRW-XLM',
                'CRIX.UPBIT.KRW-ARDR',
                'CRIX.UPBIT.KRW-KMD',
                'CRIX.UPBIT.KRW-ARK',
                'CRIX.UPBIT.KRW-STORJ',
                'CRIX.UPBIT.KRW-GRS',
                'CRIX.UPBIT.KRW-VTC',
                'CRIX.UPBIT.KRW-REP',
                'CRIX.UPBIT.KRW-EMC2',
                'CRIX.UPBIT.KRW-ADA',
                'CRIX.UPBIT.KRW-SBD',
                'CRIX.UPBIT.KRW-TIX',
                'CRIX.UPBIT.KRW-POWR',
                'CRIX.UPBIT.KRW-MER',
                'CRIX.UPBIT.KRW-BTG',
                'CRIX.UPBIT.BTC-NEO',
                'CRIX.UPBIT.BTC-BCC',
                'CRIX.UPBIT.BTC-ETH',
                'CRIX.UPBIT.BTC-MTL',
                'CRIX.UPBIT.BTC-LTC',
                'CRIX.UPBIT.BTC-STRAT',
                'CRIX.UPBIT.BTC-XRP',
                'CRIX.UPBIT.BTC-ETC',
                'CRIX.UPBIT.BTC-OMG',
                'CRIX.UPBIT.BTC-CVC',
                'CRIX.UPBIT.BTC-DGB',
                'CRIX.UPBIT.BTC-PAY',
                'CRIX.UPBIT.BTC-SC',
                'CRIX.UPBIT.BTC-SNT',
                'CRIX.UPBIT.BTC-DASH',
                'CRIX.UPBIT.BTC-XVG',
                'CRIX.UPBIT.BTC-WAVES',
                'CRIX.UPBIT.BTC-NMR',
                'CRIX.UPBIT.BTC-SYNX',
                'CRIX.UPBIT.BTC-PIVX',
                'CRIX.UPBIT.BTC-GBYTE',
                'CRIX.UPBIT.BTC-XEM',
                'CRIX.UPBIT.BTC-FUN',
                'CRIX.UPBIT.BTC-ZEC',
                'CRIX.UPBIT.BTC-XMR',
                'CRIX.UPBIT.BTC-LBC',
                'CRIX.UPBIT.BTC-QTUM',
                'CRIX.UPBIT.BTC-GNT',
                'CRIX.UPBIT.BTC-NXT',
                'CRIX.UPBIT.BTC-BAT',
                'CRIX.UPBIT.BTC-XEL',
                'CRIX.UPBIT.BTC-EDG',
                'CRIX.UPBIT.BTC-LSK',
                'CRIX.UPBIT.BTC-RDD',
                'CRIX.UPBIT.BTC-DCT',
                'CRIX.UPBIT.BTC-STEEM',
                'CRIX.UPBIT.BTC-GAME',
                'CRIX.UPBIT.BTC-FCT',
                'CRIX.UPBIT.BTC-PTOY',
                'CRIX.UPBIT.BTC-DCR',
                'CRIX.UPBIT.BTC-DOGE',
                'CRIX.UPBIT.BTC-BNT',
                'CRIX.UPBIT.BTC-XLM',
                'CRIX.UPBIT.BTC-PART',
                'CRIX.UPBIT.BTC-MCO',
                'CRIX.UPBIT.BTC-UBQ',
                'CRIX.UPBIT.BTC-ARDR',
                'CRIX.UPBIT.BTC-KMD',
                'CRIX.UPBIT.BTC-ARK',
                'CRIX.UPBIT.BTC-ADX',
                'CRIX.UPBIT.BTC-SYS',
                'CRIX.UPBIT.BTC-ANT',
                'CRIX.UPBIT.BTC-MUE',
                'CRIX.UPBIT.BTC-XDN',
                'CRIX.UPBIT.BTC-STORJ',
                'CRIX.UPBIT.BTC-QRL',
                'CRIX.UPBIT.BTC-NXS',
                'CRIX.UPBIT.BTC-GRS',
                'CRIX.UPBIT.BTC-VOX',
                'CRIX.UPBIT.BTC-VTC',
                'CRIX.UPBIT.BTC-CLOAK',
                'CRIX.UPBIT.BTC-SIB',
                'CRIX.UPBIT.BTC-REP',
                'CRIX.UPBIT.BTC-VIA',
                'CRIX.UPBIT.BTC-WINGS',
                'CRIX.UPBIT.BTC-CFI',
                'CRIX.UPBIT.BTC-1ST',
                'CRIX.UPBIT.BTC-UNB',
                'CRIX.UPBIT.BTC-NBT',
                'CRIX.UPBIT.BTC-SWT',
                'CRIX.UPBIT.BTC-MAID',
                'CRIX.UPBIT.BTC-SLS',
                'CRIX.UPBIT.BTC-AGRS',
                'CRIX.UPBIT.BTC-MONA',
                'CRIX.UPBIT.BTC-AMP',
                'CRIX.UPBIT.BTC-HMQ',
                'CRIX.UPBIT.BTC-SNGLS',
                'CRIX.UPBIT.BTC-TX',
                'CRIX.UPBIT.BTC-RLC',
                'CRIX.UPBIT.BTC-BLOCK',
                'CRIX.UPBIT.BTC-DYN',
                'CRIX.UPBIT.BTC-GUP',
                'CRIX.UPBIT.BTC-MEME',
                'CRIX.UPBIT.BTC-OK',
                'CRIX.UPBIT.BTC-XZC',
                'CRIX.UPBIT.BTC-ADT',
                'CRIX.UPBIT.BTC-FTC',
                'CRIX.UPBIT.BTC-ION',
                'CRIX.UPBIT.BTC-BSD',
                'CRIX.UPBIT.BTC-GNO',
                'CRIX.UPBIT.BTC-DGD',
                'CRIX.UPBIT.BTC-EMC2',
                'CRIX.UPBIT.BTC-EXCL',
                'CRIX.UPBIT.BTC-SPHR',
                'CRIX.UPBIT.BTC-EXP',
                'CRIX.UPBIT.BTC-XAUR',
                'CRIX.UPBIT.BTC-BITB',
                'CRIX.UPBIT.BTC-BAY',
                'CRIX.UPBIT.BTC-VRC',
                'CRIX.UPBIT.BTC-BURST',
                'CRIX.UPBIT.BTC-SHIFT',
                'CRIX.UPBIT.BTC-BLK',
                'CRIX.UPBIT.BTC-ZEN',
                'CRIX.UPBIT.BTC-KORE',
                'CRIX.UPBIT.BTC-RADS',
                'CRIX.UPBIT.BTC-MYST',
                'CRIX.UPBIT.BTC-IOP',
                'CRIX.UPBIT.BTC-RISE',
                'CRIX.UPBIT.BTC-NAV',
                'CRIX.UPBIT.BTC-ADA',
                'CRIX.UPBIT.BTC-MANA',
                'CRIX.UPBIT.BTC-SALT',
                'CRIX.UPBIT.BTC-SBD',
                'CRIX.UPBIT.BTC-TIX',
                'CRIX.UPBIT.BTC-RCN',
                'CRIX.UPBIT.BTC-VIB',
                'CRIX.UPBIT.BTC-POWR',
                'CRIX.UPBIT.BTC-MER',
                'CRIX.UPBIT.BTC-BTG',
                'CRIX.UPBIT.ETH-NEO',
                'CRIX.UPBIT.ETH-BCC',
                'CRIX.UPBIT.ETH-MTL',
                'CRIX.UPBIT.ETH-LTC',
                'CRIX.UPBIT.ETH-STRAT',
                'CRIX.UPBIT.ETH-XRP',
                'CRIX.UPBIT.ETH-ETC',
                'CRIX.UPBIT.ETH-OMG',
                'CRIX.UPBIT.ETH-CVC',
                'CRIX.UPBIT.ETH-DGB',
                'CRIX.UPBIT.ETH-PAY',
                'CRIX.UPBIT.ETH-SC',
                'CRIX.UPBIT.ETH-SNT',
                'CRIX.UPBIT.ETH-DASH',
                'CRIX.UPBIT.ETH-WAVES',
                'CRIX.UPBIT.ETH-NMR',
                'CRIX.UPBIT.ETH-XEM',
                'CRIX.UPBIT.ETH-FUN',
                'CRIX.UPBIT.ETH-ZEC',
                'CRIX.UPBIT.ETH-XMR',
                'CRIX.UPBIT.ETH-QTUM',
                'CRIX.UPBIT.ETH-GNT',
                'CRIX.UPBIT.ETH-BAT',
                'CRIX.UPBIT.ETH-FCT',
                'CRIX.UPBIT.ETH-PTOY',
                'CRIX.UPBIT.ETH-BNT',
                'CRIX.UPBIT.ETH-XLM',
                'CRIX.UPBIT.ETH-MCO',
                'CRIX.UPBIT.ETH-ADX',
                'CRIX.UPBIT.ETH-ANT',
                'CRIX.UPBIT.ETH-STORJ',
                'CRIX.UPBIT.ETH-QRL',
                'CRIX.UPBIT.ETH-REP',
                'CRIX.UPBIT.ETH-WINGS',
                'CRIX.UPBIT.ETH-CFI',
                'CRIX.UPBIT.ETH-1ST',
                'CRIX.UPBIT.ETH-HMQ',
                'CRIX.UPBIT.ETH-SNGLS',
                'CRIX.UPBIT.ETH-RLC',
                'CRIX.UPBIT.ETH-GUP',
                'CRIX.UPBIT.ETH-ADT',
                'CRIX.UPBIT.ETH-GNO',
                'CRIX.UPBIT.ETH-DGD',
                'CRIX.UPBIT.ETH-MYST',
                'CRIX.UPBIT.ETH-MANA',
                'CRIX.UPBIT.ETH-SALT',
                'CRIX.UPBIT.ETH-TIX',
                'CRIX.UPBIT.ETH-RCN',
                'CRIX.UPBIT.ETH-VIB',
                'CRIX.UPBIT.ETH-POWR',
                'CRIX.UPBIT.ETH-BTG',
                'CRIX.UPBIT.USDT-BTC',
                'CRIX.UPBIT.USDT-NEO',
                'CRIX.UPBIT.USDT-BCC',
                'CRIX.UPBIT.USDT-ETH',
                'CRIX.UPBIT.USDT-LTC',
                'CRIX.UPBIT.USDT-XRP',
                'CRIX.UPBIT.USDT-ETC',
                'CRIX.UPBIT.USDT-DASH',
                'CRIX.UPBIT.USDT-ZEC',
                'CRIX.UPBIT.USDT-XMR',
                'CRIX.UPBIT.USDT-OMG',
                'CRIX.UPBIT.USDT-BTG',
                'CRIX.UPBIT.USDT-NXT',
                'CRIX.UPBIT.USDT-ADA',
                'CRIX.UPBIT.USDT-XVG',
                'CRIX.COINMARKETCAP.KRW-USDT',
            ]
        }]
        self._transaction_history = {}
        self._usdkrw = 0.0

    def on_msg(self, ws, msg):
        if msg == 'o':
            ws.send(json.dumps([json.dumps(self._data)]))
        elif msg[0] == 'a':
            entry = json.loads(json.loads(msg[1:])[0])

            if entry['code'].find('UPBIT') < 0:
                if entry['code'] == 'CRIX.COINMARKETCAP.KRW-USDT':
                    self._usdkrw = entry['tradePrice']

                return

            now = int(time.time())
            code = entry['code'][entry['code'].rfind('.') + 1:]
            currency = code[:code.find('-')]
            coin = code[code.find('-') + 1:]

            history = self._transaction_history.get(currency, None)
            if history is None:
                self._transaction_history[currency] = {}
                history = {}

            history = history.get(coin, None)
            if history is None:
                self._transaction_history[currency][coin] = [{
                    'tradePrice': entry['tradePrice'],
                    'timestamp': now
                }]
                return

            i = 0
            while (now - history[i]['timestamp']) >= 300:
                i += 1

            history = history[i:]
            history.append({
                'tradePrice': entry['tradePrice'],
                'timestamp': now
            })

            self._transaction_history[currency][coin] = history

    def on_err(self, ws, error):
        print "CoinAnalyzer error: {}".format(error)

    def on_close(self, ws):
        pass

    def usdkrw(self):
        return self._usdkrw

    def history(self, currency, t):
        now = int(time.time())
        result = {}

        for coin, history in self._transaction_history.get(currency, {}).items():
            if history is None:
                continue

            i = 0
            while i < len(history) and (now - history[i]['timestamp']) >= t:
                i += 1

            result[coin] = history[i:]

        return result

    def ranking(self, currency, t, n):
        result = []
        now = int(time.time())

        for coin, history in self.history(currency, t).items():
            if len(history) < 2:
                continue

            max_price, max_ts = -1, 0
            min_price, min_ts = 9999999999, 0

            for h in history:
                if h['tradePrice'] > max_price:
                    max_price = h['tradePrice']
                    max_ts = h['timestamp']
                if h['tradePrice'] < min_price:
                    min_price = h['tradePrice']
                    min_ts = h['timestamp']

            # increased
            if max_ts >= min_ts:
                rate = (max_price / min_price) - 1.0
            else:
                rate = (min_price / max_price) - 1.0

            if currency == 'KRW':
                min_price = int(min_price)
                max_price = int(max_price)

            result.append({
                'coin': coin,
                'rate': rate,
                'minPrice': min_price,
                'maxPrice': max_price,
                'elapsed': now - history[0]['timestamp']
            })

        return sorted(result, key=operator.itemgetter('rate'), reverse=True)[:n]

    def run(self):
        while True:
            self._ws = websocket.WebSocketApp(self._host, on_message=self.on_msg, on_error=self.on_err, on_close=self.on_close)
            self._ws.run_forever()

def request_coin_info(code):
    wc = WebClient("https://crix-api-endpoint.upbit.com")
    wc.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0")
    return wc.get("/v1/crix/trades/ticks", code=code, count=1)

def request_coin_info_lines(code):
    wc = WebClient("https://crix-api-endpoint.upbit.com")
    wc.add_header("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:58.0) Gecko/20100101 Firefox/58.0")
    return wc.get("/v1/crix/candles/lines", code=code)

class CoinCommand(Command):
    def __init__(self, trigger, analyzer):
        super(CoinCommand, self).__init__(trigger)
        self._analyzer = analyzer

    def description(self):
        return "코인 시장을 분석한다."

    def usage(self):
        cmd = self.trigger()
        m = "'/{0}': 코인의 가격 변동 순위 혹은 현재 코인 시세를 출력한다\n\n".format(cmd)
        m += "'/{0} <시간> <통화>': <시간>동안의 코인 가격 변동 순위를 보여줍니다\n".format(cmd)
        m += "  <시간>은 초 단위이며 5~300 사이의 값을 가집니다.\n"
        m += "  <통화>는 출력할 코인의 기준 통화입니다.\n"
        m += "  입력 가능한 통화는 krw, btc, eth, usdt 입니다. (기본값 krw)\n\n"
        m += "'/{0} 김프': 현재 김프 상황을 보여줍니다\n".format(cmd)
        m += "  현재의 김프 현황을 출력합니다.\n"
        m += "'/{0} 김프 <시간>': 약 <시간> * 15분 전 김프 상황을 보여줍니다\n".format(cmd)
        m += "  <시간> * 15분 전의 김프 현황을 출력합니다.\n"
        m += "  서버가 15분 주기로 데이터를 저장하므로 명령 시점으로부터 오차가 발생할 수 있습니다\n\n"
        m += "'/{0} <통화>': <통화>의 현재 시세를 보여줍니다\n".format(cmd)
        m += "  <통화>는 코인의 고유 코드에 기준 통화(기본 KRW)를 선택적으로 이어서 쓸 수 있습니다\n"
        m += "  ex) /{0} steem (STEEM/KRW의 시세 출력)\n".format(cmd)
        m += "  ex) /{0} bccbtc (BCC/BTC의 시세 출력)".format(cmd)

        return m

    def run(self, sess, args, chat):
        chat_id = chat.chat_id()
        try:
            coin_or_time = args.pop(0)
            if coin_or_time.isdigit():
                t = int(coin_or_time)
                if t < 5 or t > 300:
                    sess.send_text("시간은 5~300 사이의 값으로 입력하세요", chat_id)
                    return

                if len(args) == 0:
                    currency = "KRW"
                else:
                    currency = args.pop(0).upper()
                    if currency not in ["KRW", "BTC", "ETH", "USDT"]:
                        sess.send_text("통화는 KRW, BTC, ETH, USDT 중 하나를 입력하세요", chat_id)
                        return

                ranking = self._analyzer.ranking(currency, t, 10)
                rank = 1
                msg = "코인 순위 - {}\n".format(currency)

                if len(ranking) == 0:
                    msg += "\n집계된 데이터가 없습니다"
                else:
                    msg += "집계 기준: 약 {}초 전부터 지금까지\n\n".format(ranking[0]["elapsed"])

                    if currency == "KRW":
                        msg_format = "{}. {} - {:,} -> {:,} ({:.2f}%)\n"
                    elif currency == "USDT":
                        msg_format = "{}. {} - {:,.3f} -> {:,.3f} ({:.2f}%)\n"
                    else:
                        msg_format = "{}. {} - {:.8f} -> {:.8f} ({:.2f}%)\n"

                    for coin in ranking:
                        if coin["rate"] < 0.0:
                            msg += msg_format.format(rank, coin["coin"], coin["maxPrice"], coin["minPrice"], coin["rate"] * 100.0)
                        else:
                            msg += msg_format.format(rank, coin["coin"], coin["minPrice"], coin["maxPrice"], coin["rate"] * 100.0)
                        rank += 1

                sess.send_text(msg.strip(), chat_id)
            elif coin_or_time == "김프":
                if len(args) > 0:
                    n = args.pop(0)
                    if n.isdigit():
                        n = int(n)
                        if n < 0:
                            n = 0
                    else:
                        n = 0
                else:
                    n = 0

                targets = [
                    "CRIX.UPBIT.{}-BTC",
                    "CRIX.UPBIT.{}-ETH",
                    "CRIX.UPBIT.{}-XRP",
                    "CRIX.UPBIT.{}-BTG",
                    "CRIX.UPBIT.{}-LTC",
                    "CRIX.UPBIT.{}-NEO",
                ]

                threads = []
                request_func = request_coin_info if n == 0 else request_coin_info_lines

                for target in targets:
                    code = target.format("KRW")
                    threads.append(gevent.spawn(request_func, code))

                    code = target.format("USDT")
                    threads.append(gevent.spawn(request_func, code))

                gevent.joinall(threads)

                if n == 0:
                    entry = threads[0].value[0]
                    date = "{} {}".format(entry["tradeDateKst"], entry["tradeTimeKst"])
                else:
                    max_idx = len(threads[0].value["candles"]) - 1
                    if n > max_idx:
                        n = max_idx
                    entry = threads[0].value["candles"][n - 1]
                    date = entry["candleDateTimeKst"].split("+")[0].replace("T", " ")

                msg = "김치프리미엄 현황\n"
                msg += "조회 시간: {}\n".format(date)
                msg += "적용 환율: {:,}원\n\n".format(int(self._analyzer.usdkrw()))

                for i in xrange(0, len(threads), 2):
                    if n == 0:
                        krw_result = threads[i].value[0]
                        usdt_result = threads[i + 1].value[0]
                    else:
                        krw_result = threads[i].value["candles"][n - 1]
                        usdt_result = threads[i + 1].value["candles"][n - 1]

                    coin = krw_result["code"][krw_result["code"].rfind("-") + 1:]

                    krw = krw_result["tradePrice"]
                    usdkrw = usdt_result["tradePrice"] * self._analyzer.usdkrw()
                    premium = (krw / usdkrw - 1) * 100
                    msg += "{}. {} - {:.2f}%\n".format(i / 2 + 1, coin, premium)

                sess.send_text(msg.strip(), chat_id)
            else:
                coin = coin_or_time.upper()

                if (coin[-3:] == 'KRW' or coin[-3:] == 'BTC' or coin[-3:] == 'ETH') and len(coin) > 3:
                    code = 'CRIX.UPBIT.' + coin[-3:] + '-' + coin[:-3]
                elif coin[-4:] == 'USDT':
                    code = 'CRIX.UPBIT.' + coin[-4:] + '-' + coin[:-4]
                else:
                    code = 'CRIX.UPBIT.KRW-' + coin

                thread = gevent.spawn(request_coin_info, code)
                thread.join()
                result = thread.value

                if result == "":
                    msg = "없는 코인: {}".format(coin)
                    sess.send_text(msg, chat_id)
                else:
                    result = result[0]
                    coin = result["code"][result["code"].rfind(".") + 1:]
                    currency = coin.split('-')[0]
                    if currency == "KRW":
                        result["tradePrice"] = int(result["tradePrice"])
                        price = "{:,}"
                    elif currency == "USDT":
                        price = "{:,.3f}"
                    else:
                        price = "{:.8f}"

                    msg = "{} 시세\n\n".format("/".join(coin.split("-")[::-1]))
                    msg += "조회 시간: {} {}\n".format(result["tradeDateKst"], result["tradeTimeKst"])
                    msg += "현재 가격: " + price.format(result["tradePrice"])

                    sess.send_text(msg, chat_id)
        except:
            import traceback
            print traceback.format_exc()
            sess.send_text(self.usage(), chat_id)
