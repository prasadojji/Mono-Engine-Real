import requests
import csv
from io import StringIO
from datetime import datetime, date
import time
import threading

import requests
from requests.exceptions import HTTPError

from mono_engine.config import Config
from mono_engine.core.rest_client import RestClient

import logging

class Session:
    """
    Authentication/session using your proven working method (direct requests).
    """

    def __init__(self, config: Config):
        self.config = config
        self.rest = RestClient(config.endpoints.get('base_url', 'https://api.tradejini.com/v2'))
        self.logged_in = False

    def login(self) -> bool:
        creds = self.config.credentials
        apikey = creds.get('apikey')
        password = creds.get('password')
        two_fa = creds.get('two_fa', '')
        two_fa_typ = creds.get('two_fa_typ', 'totp').lower()

        if not all([apikey, password]):
            logging.error("Missing apikey or password")
            return False

        url = f"{self.rest.base_url}/api-gw/oauth/individual-token-v2"
        headers = {"Authorization": f"Bearer {apikey}"}
        payload = {"password": password}
        if two_fa:
            payload["twoFa"] = two_fa
            payload["twoFaTyp"] = two_fa_typ
            logging.info("Using 2FA (totp) in login")

        try:
            response = requests.post(url, data=payload, headers=headers, timeout=20)
            response.raise_for_status()
            data = response.json()
            access_token = data.get("access_token")
            if access_token:
                self.rest.set_auth(apikey, access_token)
                self.logged_in = True
                logging.info("LOGIN SUCCESSFUL! Access token received")
                return True
            else:
                logging.error("No access_token in response: {}", data)
        except HTTPError as e:
            logging.error("Login HTTP error: {} - Response: {}", e, response.text if 'response' in locals() else "No response")
        except Exception as e:
            logging.error("Login exception: {}", str(e))

        self.logged_in = False
        return False

    def is_logged_in(self) -> bool:
        return self.logged_in

    def close(self):
        self.rest.close()

import websocket
import threading
import time
import struct
import zlib
import traceback
import errno
import json
import re
import os
import sys
from datetime import datetime

CURRENT_VERSION = 1
PKG_VERSION = '1.0.2'

def commafmt(value, precision=2):
    v = str(round(float(value), 2))
    parts = v.split(".")
    parts[0] = re.sub("\B(?=(\d{3})+(?!\d))", ",", parts[0])
    return ".".join(parts)


def divide(value, divisor=100.0):
    return value / float(divisor)


def datefmt(value):
    if value is None:
        return value
    date_time = datetime.fromtimestamp(value)
    return str(date_time)


L1 = "L1"
L5 = "L5"
OHLC = "OHLC"
AUTH = "auth"
MARKET_STATUS = "marketStatus"
EVENTS = "EVENTS"
PING = "PING"
GREEKS = "greeks"

SEG_INFO = {
    1: {"exchSeg": "NSE", "precision": 2, "divisor": 100.0},
    2: {"exchSeg": "BSE", "precision": 2, "divisor": 100.0},
    3: {"exchSeg": "NFO", "precision": 2, "divisor": 100.0},
    4: {"exchSeg": "BFO", "precision": 2, "divisor": 100.0},
    5: {"exchSeg": "CDS", "precision": 4, "divisor": 10000000.0},
    6: {"exchSeg": "BCD", "precision": 4, "divisor": 10000.0},
    7: {"exchSeg": "MCD", "precision": 4, "divisor": 10000.0},
    8: {"exchSeg": "MCX", "precision": 2, "divisor": 100.0},
    9: {"exchSeg": "NCO", "precision": 2, "divisor": 10000.0},
    10: {"exchSeg": "BCO", "precision": 2, "divisor": 10000.0}
}
PKT_TYPE = {
    10: L1,
    11: L5,
    12: OHLC,
    13: AUTH,
    14: MARKET_STATUS,
    15: EVENTS,
    16: PING,
    17: GREEKS
}

# spec format :: 67: {  "struct":"d", "key": "ltp", "len": 8, "fmt": lambda v, p :  commafmt(v, p) },
DEFAULT_PKT_INFO = {
    "PKT_SPEC": {
        10: {
            26: {"struct": "B", "key": "exchSeg", "len": 1},
            27: {"struct": "i", "key": "token", "len": 4},
            28: {"struct": "B", "key": "precision", "len": 1},
            29: {"struct": "i", "key": "ltp", "len": 4, "fmt": lambda v, d: divide(v, d)},
            30: {"struct": "i", "key": "open", "len": 4, "fmt": lambda v, d: divide(v, d)},
            31: {"struct": "i", "key": "high", "len": 4, "fmt": lambda v, d: divide(v, d)},
            32: {"struct": "i", "key": "low", "len": 4, "fmt": lambda v, d: divide(v, d)},
            33: {"struct": "i", "key": "close", "len": 4, "fmt": lambda v, d: divide(v, d)},
            34: {"struct": "i", "key": "chng", "len": 4, "fmt": lambda v, d: divide(v, d)},
            35: {"struct": "i", "key": "chngPer", "len": 4, "fmt": lambda v, d: divide(v)},
            36: {"struct": "i", "key": "atp", "len": 4, "fmt": lambda v, d: divide(v, d)},
            37: {"struct": "i", "key": "yHigh", "len": 4, "fmt": lambda v, d: divide(v, d)},
            38: {"struct": "i", "key": "yLow", "len": 4, "fmt": lambda v, d: divide(v, d)},
            39: {"struct": "<I", "key": "ltq", "len": 4},
            40: {"struct": "<I", "key": "vol", "len": 4},
            41: {"struct": "d", "key": "ttv", "len": 8},
            42: {"struct": "i", "key": "ucl", "len": 4, "fmt": lambda v, d: divide(v, d)},
            43: {"struct": "i", "key": "lcl", "len": 4, "fmt": lambda v, d: divide(v, d)},
            44: {"struct": "<I", "key": "OI", "len": 4},
            45: {"struct": "i", "key": "OIChngPer", "len": 4, "fmt": lambda v, d: divide(v)},
            46: {"struct": "i", "key": "ltt", "len": 4, "fmt": lambda v: datefmt(v)},
            49: {"struct": "i", "key": "bidPrice", "len": 4, "fmt": lambda v, d: divide(v, d)},
            50: {"struct": "<I", "key": "qty", "len": 4},
            51: {"struct": "<I", "key": "no", "len": 4},
            52: {"struct": "i", "key": "askPrice", "len": 4, "fmt": lambda v, d: divide(v, d)},
            53: {"struct": "<I", "key": "qty", "len": 4},
            54: {"struct": "<I", "key": "no", "len": 4},
            55: {"struct": "B", "key": "nDepth", "len": 1},
            56: {"struct": "H", "key": "nLen", "len": 2},
            58: {"struct": "<I", "key": "prevOI", "len": 4},
            59: {"struct": "<I", "key": "dayHighOI", "len": 4},
            60: {"struct": "<I", "key": "dayLowOI", "len": 4},
            70: {"struct": "i", "key": "spotPrice", "len": 4, "fmt": lambda v, d: divide(v, d)},
            71: {"struct": "i", "key": "dayClose", "len": 4, "fmt": lambda v, d: divide(v, d)},
            74: {"struct": "i", "key": "vwap", "len": 4, "fmt": lambda v, d: divide(v, d)},
        },
        11: {
            26: {"struct": "B", "key": "exchSeg", "len": 1},
            27: {"struct": "i", "key": "token", "len": 4},
            28: {"struct": "B", "key": "precision", "len": 1},
            47: {"struct": "<I", "key": "totBuyQty", "len": 4},
            48: {"struct": "<I", "key": "totSellQty", "len": 4},
            49: {"struct": "i", "key": "price", "len": 4, "fmt": lambda v, d: divide(v, d)},
            50: {"struct": "<I", "key": "qty", "len": 4},
            51: {"struct": "<I", "key": "no", "len": 4},
            52: {"struct": "i", "key": "price", "len": 4, "fmt": lambda v, d: divide(v, d)},
            53: {"struct": "<I", "key": "qty", "len": 4},
            54: {"struct": "<I", "key": "no", "len": 4},
            55: {"struct": "B", "key": "nDepth", "len": 1},
        },
        12: {
            26: {"struct": "B", "key": "exchSeg", "len": 1},
            27: {"struct": "i", "key": "token", "len": 4},
            28: {"struct": "B", "key": "precision", "len": 1},
            30: {"struct": "i", "key": "open", "len": 4, "fmt": lambda v, d: divide(v, d)},
            31: {"struct": "i", "key": "high", "len": 4, "fmt": lambda v, d: divide(v, d)},
            32: {"struct": "i", "key": "low", "len": 4, "fmt": lambda v, d: divide(v, d)},
            33: {"struct": "i", "key": "close", "len": 4, "fmt": lambda v, d: divide(v, d)},
            40: {"struct": "<I", "key": "vol", "len": 4},
            46: {"struct": "i", "key": "time", "len": 4, "fmt": lambda v: datefmt(v)},
            74: {"struct": "i", "key": "vwap", "len": 4, "fmt": lambda v, d: divide(v, d)},
            75: {"struct": "string", "key": "type", "len": 4},
            76: {"struct": "<I", "key": "minuteOi", "len": 4},
        },
        13: {
            25: {"struct": "B", "key": "auth_status", "len": 1},
        },
        14: {
            56: {"struct": "H", "key": "nLen", "len": 2},
            26: {"struct": "B", "key": "exchSeg", "len": 1},
            57: {"struct": "B", "key": "marketStatus", "len": 1},
        },
        15: {
            56: {"struct": "H", "key": "nLen", "len": 2},
            # length will be dynamiccaly altered from message
            61: {"struct": "string", "key": "message", "len": 100},
        },
        16: {
            62: {"struct": "B", "key": "pong", "len": 1},
        },
        17: {
            26: {"struct": "B", "key": "exchSeg", "len": 1},
            27: {"struct": "i", "key": "token", "len": 4},
            63: {"struct": "d", "key": "itm", "len": 8},
            64: {"struct": "d", "key": "iv", "len": 8},
            65: {"struct": "d", "key": "delta", "len": 8},
            66: {"struct": "d", "key": "gamma", "len": 8},
            67: {"struct": "d", "key": "theta", "len": 8},
            68: {"struct": "d", "key": "rho", "len": 8},
            69: {"struct": "d", "key": "vega", "len": 8},
            72: {"struct": "d", "key": "highiv", "len": 8},
            73: {"struct": "d", "key": "lowiv", "len": 8},
        }
    },
    "BID_ASK_OBJ_LEN": 3,
    "MARKET_STATUS_OBJ_LEN": 2
}


class NxtradStream:
    def __init__(self, url, version='3.1', stream_cb=None, connect_cb=None):
        self.ws = None
        self.isConnected = False

        self.stream_cb = stream_cb
        self.connect_cb = connect_cb

        self.host = "wss://" + url + "/v2.1/stream"

        self.L1_dict = {}
        self.token = ''
        self.version = version

    def connect(self, token):
        self.token = token
        self.__tryConnect()

    def reconnect(self):
        if not self.token:
            sys.exit('Unable to connect auth token is empty')
        if self.isConnected:
            print('Socket already connected')
            return
        print("Reconnecting...")
        self.__tryConnect()

    def __tryConnect(self):
        url = self.host + "?token=" + self.token + "&version=" + self.version
        # websocket.enableTrace(True)
        self.ws = websocket.WebSocketApp(
            url,
            on_open=self.__on_open,
            on_message=self.__on_message,
            on_error=self.__on_error,
            on_close=self.__on_close,
        )

        threading.Thread(target=self.__task).start()

    def subscribeEvents(self, type):
        req = {}
        req["type"] = "event"
        req["action"] = "sub"

        req["events"] = type

        return self.__send_data(req)

    def sendPing(self):
        req = {}
        req["type"] = "PING"
        return self.__send_data(req)

    def subscribeL1(self, tokens):
        req = {}
        req["type"] = "L1"
        req["action"] = "sub"

        _l = []
        for i in tokens:
            _l.append({"t": i})

        req["tokens"] = _l

        return self.__send_data(req)

    def subscribeL1SnapShot(self, tokens):
        req = {}
        req["type"] = "L1S"
        req["action"] = "sub"

        _l = []
        for i in tokens:
            _l.append({"t": i})

        req["tokens"] = _l

        return self.__send_data(req)

    def subscribeL2(self, tokens):
        req = {}
        req["type"] = "L5"
        req["action"] = "sub"

        _l = []
        for i in tokens:
            _l.append({"t": i})

        req["tokens"] = _l

        return self.__send_data(req)

    def subscribeL2SnapShot(self, tokens):
        req = {}
        req["type"] = "L5S"
        req["action"] = "sub"

        _l = []
        for i in tokens:
            _l.append({"t": i})

        req["tokens"] = _l

        return self.__send_data(req)

    def subscribeGreeks(self, tokens):
        req = {}
        req["type"] = "greeks"
        req["action"] = "sub"

        _l = []
        for i in tokens:
            _l.append({"t": i})

        req["tokens"] = _l

        return self.__send_data(req)

    def subscribeGreeksSnapShot(self, tokens):
        req = {}
        req["type"] = "greeks-snapshot"
        req["action"] = "sub"

        _l = []
        for i in tokens:
            _l.append({"t": i})

        req["tokens"] = _l

        return self.__send_data(req)

    def unsubscribeEvents(self):
        req = {}
        req["type"] = "event"
        req["action"] = "unsub"

        return self.__send_data(req)

    def unsubscribeL1(self):

        self.L1_dict.clear()

        req = {}
        req["type"] = "L1"
        req["action"] = "unsub"

        return self.__send_data(req)

    def unsubscribeL2(self):
        req = {}
        req["type"] = "L5"
        req["action"] = "unsub"

        return self.__send_data(req)

    def unsubscribeGreeks(self):
        req = {}
        req["type"] = "greeks"
        req["action"] = "unsub"

        return self.__send_data(req)

    def subscribeOHLC(self, tokens, interval):
        req = {}
        req["type"] = "OHLC"
        req["action"] = "sub"

        _l = []
        for i in tokens:
            _l.append({"t": i})

        req["tokens"] = _l
        req["chartInterval"] = interval

        return self.__send_data(req)

    def unsubscribeOHLC(self,interval):
        req = {}
        req["type"] = "OHLC"
        req["action"] = "unsub"
        req["chartInterval"] = interval

        return self.__send_data(req)

    def disconnect(self):
        self.ws.close()
        self.isConnected = False

    def isConnected(self):
        return self.isConnected

    def __send_data(self, req):
        if not self.isConnected:
            return False

        r = json.dumps(req)
        # print(r);
        self.ws.send(r + "\n")
        return True

    def __frame_from_spec(self, spec, data, idx):
        binaryKey = spec["struct"]
        binaryLen = spec["len"]

        parsed = None
        if binaryKey == "string":
            parsed = self.__ab2str(data, idx, binaryLen)
        else:
            parsed = struct.unpack(binaryKey, data[idx: idx + binaryLen])[0]

        return parsed

    def __format_values(self, divisor, raw_data, jData):
        for key, value in raw_data.items():
            spec = value[0]
            framed = value[1]
            jData[spec["key"]] = (spec["fmt"](
                framed, divisor) if "fmt" in spec else framed)

    def __ab2str(self, buf, offset, length):
        unpacklen = str(length) + "s"
        v = struct.unpack(unpacklen, buf[offset: offset + length])
        res = v[0].rstrip(b'\x00').decode("utf_8")
        return res

    def __onsinglePacket(self, data, data_len):
        pktType = struct.unpack("b", data[2:3])[0]
        pktSpec = DEFAULT_PKT_INFO["PKT_SPEC"]
        if pktType not in pktSpec:
            print("Unknown PktType : ", pktType)
            return

        packetType = PKT_TYPE[pktType]
        quoteSpec = pktSpec[pktType]
        jData = None
        if packetType == L1:
            jData = self.__decodeL1PKT(quoteSpec, data_len, data)
        elif packetType == L5:
            jData = self.__decodeL2PKT(quoteSpec, data_len, data)
        elif packetType == OHLC:
            jData = self.__decodeOHLC(quoteSpec, data_len, data)
        elif packetType == MARKET_STATUS:
            jData = self.__decodeMarketStatus(quoteSpec, data_len, data)
        elif packetType == EVENTS:
            jData = self.__decodeMessage(quoteSpec, data_len, data)
        elif packetType == PING:
            jData = self.__decodeStatus(quoteSpec, data_len, data)
        elif packetType == GREEKS:
            jData = self.__decodeL1PKT(quoteSpec, data_len, data)

        if jData is not None:
            jData["msgType"] = packetType

            if packetType == L1:
                t = jData["symbol"]
                if t in self.L1_dict:
                    _cache_d = self.L1_dict[t]
                    _cache_d.update(jData)
                    jData = _cache_d
                self.L1_dict[t] = jData

            self._callback(self.stream_cb, self, jData)

    def __decodeL1PKT(self, pktSpec, data_len, data):
        jData = {}
        raw_data = {}
        exchange_info = None
        divisor = 100.0
        precision = 2
        idx = 3
        while idx < data_len:
            pktKey = struct.unpack("B", data[idx: idx + 1])
            idx += 1
            spec = pktSpec[pktKey[0]]
            framed = self.__frame_from_spec(spec, data, idx)
            if spec["key"] == "exchSeg":
                exchange_info = SEG_INFO[framed]
                precision = exchange_info["precision"]
                divisor = exchange_info["divisor"]
                jData[spec["key"]] = exchange_info["exchSeg"]
            elif spec["key"] == "ltt":
                jData[spec["key"]] = (spec["fmt"](
                    framed) if "fmt" in spec else framed)
            else:
                raw_data[spec["key"]] = (spec, framed)

            idx += spec["len"]

        if (exchange_info is not None):
            self.__format_values(divisor, raw_data, jData)

        jData["symbol"] = str(jData["token"]) + "_" + jData["exchSeg"]
        jData["precision"] = precision

        return jData

    def __decodeL2PKT(self, pktSpec, data_len, data):
        exchange_info = None
        raw_data = {}
        divisor = 100.0
        precision = 2
        noLevel = 0
        bids = []
        asks = []
        list = None
        lObj = {}
        jData = {}
        idx = 3
        while idx < data_len:
            pktKey = struct.unpack("B", data[idx: idx + 1])
            idx += 1
            spec = pktSpec[pktKey[0]]
            framed = self.__frame_from_spec(spec, data, idx)
            if spec["key"] == "nDepth":
                noLevel = framed
                list = bids
            elif spec["key"] == "exchSeg":
                exchange_info = SEG_INFO[framed]
                precision = exchange_info["precision"]
                divisor = exchange_info["divisor"]
                jData[spec["key"]] = exchange_info["exchSeg"]
            else:
                if (list is not None):
                    lObj[spec["key"]] = (
                        spec["fmt"](
                            framed, divisor) if "fmt" in spec else framed
                    )
                else:
                    raw_data[spec["key"]] = (spec, framed)

            if list is not None:
                if len(lObj) == DEFAULT_PKT_INFO["BID_ASK_OBJ_LEN"]:
                    list.append(lObj)
                    lObj = {}
                if noLevel == len(list):
                    list = asks

            idx += spec["len"]

        if (exchange_info is not None):
            self.__format_values(divisor, raw_data, jData)

        jData["bid"] = bids
        jData["ask"] = asks
        jData["precision"] = precision
        jData["symbol"] = str(jData["token"]) + "_" + jData["exchSeg"]
        return jData

    def __decodeOHLC(self, pktSpec, data_len, data):
        jData = {}
        raw_data = {}
        exchange_info = None
        divisor = 100.0
        precision = 2
        idx = 3
        while idx < data_len:
            pktKey = struct.unpack("B", data[idx: idx + 1])
            idx += 1
            spec = pktSpec[pktKey[0]]
            framed = self.__frame_from_spec(spec, data, idx)
            if spec["key"] == "exchSeg":
                exchange_info = SEG_INFO[framed]
                precision = exchange_info["precision"]
                divisor = exchange_info["divisor"]
                jData[spec["key"]] = exchange_info["exchSeg"]
            elif spec["key"] == "time":
                jData[spec["key"]] = (spec["fmt"](
                    framed) if "fmt" in spec else framed)
            else:
                raw_data[spec["key"]] = (spec, framed)

            idx += spec["len"]

        if (exchange_info is not None):
            self.__format_values(divisor, raw_data, jData)

        jData["symbol"] = str(jData["token"]) + "_" + jData["exchSeg"]
        jData["precision"] = precision

        return jData

    def __decodeMarketStatus(self, pktSpec, data_len, data):
        lObj = {}
        jData = {}
        idx = 3
        noOfLen = 0
        exchange_info = None
        list = None
        while idx < data_len:
            pktKey = struct.unpack("B", data[idx: idx + 1])
            idx += 1
            spec = pktSpec[pktKey[0]]
            framed = self.__frame_from_spec(spec, data, idx)
            if spec["key"] == "nLen":
                noOfLen = framed
                list = []
            else:
                lObj[spec["key"]] = framed
                if (spec["key"] == "exchSeg"):
                    exchange_info = SEG_INFO[framed]
                    lObj[spec["key"]] = exchange_info["exchSeg"]

            if list is not None:
                if len(lObj) == DEFAULT_PKT_INFO["MARKET_STATUS_OBJ_LEN"]:
                    list.append(lObj)
                    lObj = {}

            idx += spec["len"]

        jData["status"] = list
        return jData

    def __decodeMessage(self, pktSpec, data_len, data):
        jData = {}
        idx = 3
        noOfLen = 0
        while idx < data_len:
            pktKey = struct.unpack("B", data[idx: idx + 1])
            idx += 1
            spec = pktSpec[pktKey[0]]
            framed = self.__frame_from_spec(spec, data, idx)
            if spec["key"] == "nLen":
                noOfLen = framed
                pktSpec[61]["len"] = noOfLen  # Setttng message len from here
            else:
                jData[spec["key"]] = framed

            idx += spec["len"]

        return jData

    def __decodeStatus(self, pktSpec, data_len, data):
        jData = {}
        idx = 3
        while idx < data_len:
            pktKey = struct.unpack("B", data[idx: idx + 1])
            idx += 1
            spec = pktSpec[pktKey[0]]
            framed = self.__frame_from_spec(spec, data, idx)
            jData[spec["key"]] = (spec["fmt"](
                framed) if "fmt" in spec else framed)
            idx += spec["len"]

        return jData

    def __decompressZLib(self, c_data):
        dc_data = zlib.decompress(c_data)
        return dc_data

    def __on_message(self, ws, message):
        totalRecivedLen = struct.unpack("i", message[:4])[0]
        version = struct.unpack("b", message[4:5])[0]
        if version != CURRENT_VERSION:
            print("Kindly download and use the updated SDK.")
            return

        compressionAlgo = struct.unpack("b", message[5:6])[0]
        dc_data = message[6:]
        if compressionAlgo == 100:
            dc_data = self.__decompressZLib(message[6:])

        totalRecivedLen = len(dc_data)
        bufferIndex = 0
        while bufferIndex < totalRecivedLen:
            pktLen = struct.unpack(
                "h", dc_data[bufferIndex: (bufferIndex + 2)])[0]
            if pktLen <= 0:
                print("Packet Length is wrong exiting the loop" + str(pktLen))
                break

            self.__onsinglePacket(
                dc_data[bufferIndex: (bufferIndex + pktLen)], pktLen)
            bufferIndex += pktLen

    def __on_error(self, ws, error):
        self.isConnected = False
        self._callback(self.connect_cb, self, {"s": "error", "reason": error})

    def __on_close(self, ws, close_status_code, close_msg):
        self.isConnected = False
        self._callback(self.connect_cb, self, {
                       "s": "closed", "code": close_status_code, "reason": close_msg})

    def __on_open(self, ws):
        self.isConnected = True
        self._callback(self.connect_cb, self, {"s": "connected"})

    def __task(self):
        self.ws.run_forever()

    def _callback(self, callback, *args):
        if callback:
            try:
                callback(*args)
            except Exception as e:
                print("Error in Calling callback {}: {}".format(callback, e))


# Global variables to share data between WebSocket callbacks and main script
sensex_open_price = None
index_token = None
index_exch_seg = None
sensex_options = []  # List of dicts: {'token': str, 'exch_seg': str, 'strike': float, 'option_type': str, 'expiry': date}

def connect_cb(nx_stream, ev):
    global index_token, index_exch_seg
    print("Connection event:", ev)
    if ev['s'] == "connected" and index_token:
        index_sym = f"{index_token}_{index_exch_seg}"
        print(f"Subscribing to L1 snapshot and stream for Sensex index: {index_sym}")
        nx_stream.subscribeL1SnapShot([index_sym])
        nx_stream.subscribeL1([index_sym])

def stream_cb(nx_stream, data):
    global sensex_open_price
    if data.get('msgType') == L1 and data.get('token') == index_token:
        open_price = data.get('open')
        if open_price and open_price > 0 and sensex_open_price is None:
            sensex_open_price = open_price
            print(f"\n=== Sensex Day Open Price: {open_price} ===\n")
            identify_atm_options()

def identify_atm_options():
    global sensex_open_price, sensex_options
    if not sensex_open_price or not sensex_options:
        print("No open price or options data yet.")
        return

    today = date.today()

    # Group options by expiry and find nearest future expiry
    expiry_groups = {}
    for opt in sensex_options:
        exp_date = opt['expiry']
        if exp_date >= today:
            expiry_groups.setdefault(exp_date, []).append(opt)

    if not expiry_groups:
        print("No active/future Sensex options found.")
        return

    nearest_expiry = min(expiry_groups.keys())
    current_opts = expiry_groups[nearest_expiry]

    # Get unique strikes for this expiry
    strikes = {opt['strike'] for opt in current_opts if opt['strike'] > 0}
    if not strikes:
        print("No strikes found for nearest expiry.")
        return

    # Find closest strike to open price (ATM approximation)
    atm_strike = min(strikes, key=lambda s: abs(s - sensex_open_price))
    print(f"Nearest Expiry: {nearest_expiry.strftime('%Y-%m-%d')}")
    print(f"ATM Strike (closest to open {sensex_open_price}): {atm_strike}")

    # Find CE and PE at ATM strike
    ce_opt = next((o for o in current_opts if o['option_type'] == 'CE' and o['strike'] == atm_strike), None)
    pe_opt = next((o for o in current_opts if o['option_type'] == 'PE' and o['strike'] == atm_strike), None)

    if ce_opt:
        print(f"ATM Call (CE) - Token: {ce_opt['token']}_{ce_opt['exch_seg']}")
    if pe_opt:
        print(f"ATM Put (PE) - Token: {pe_opt['token']}_{pe_opt['exch_seg']}")

    # Optional: Subscribe to these ATM options for live data
    tokens_to_sub = []
    if ce_opt:
        tokens_to_sub.append(f"{ce_opt['token']}_{ce_opt['exch_seg']}")
    if pe_opt:
        tokens_to_sub.append(f"{pe_opt['token']}_{pe_opt['exch_seg']}")
    if tokens_to_sub:
        print(f"Subscribing to ATM options: {tokens_to_sub}")
        nx_stream.subscribeL1(tokens_to_sub)
        nx_stream.subscribeL1SnapShot(tokens_to_sub)

if __name__ == "__main__":
    # === AUTHENTICATION (using your Session class) ===
    # Replace with your actual Config setup
    config = Config()  # You already have this configured
    session = Session(config)
    if not session.login():
        print("Login failed. Exiting.")
        exit(1)

    # Assuming your RestClient supports .get() returning requests.Response-like object
    rest = session.rest
    base_url = "https://api.tradejini.com/v2"

    # Get access_token (you may need to expose it in Session or fetch from config)
    # For this example, we'll use requests directly with Bearer access_token
    # Adjust if your RestClient handles auth automatically
    access_token = session.rest.access_token if hasattr(session.rest, 'access_token') else "YOUR_ACCESS_TOKEN_HERE"  # Fetch properly
    headers = {"Authorization": f"Bearer {access_token}"}

    # Fetch and save scrip masters for relevant groups
    relevant_groups = ["Securities", "Derivatives"]  # Common names based on docs/blogs
    for group in relevant_groups:
        url = f"{base_url}/api/mkt-data/scrips/symbol-store/{group}"
        resp = requests.get(url, headers={**headers, "Accept": "text/plain"})
        if resp.status_code == 200:
            with open(f"{group}.csv", "w", encoding="utf-8") as f:
                f.write(resp.text)
            print(f"Downloaded {group}.csv")
        else:
            print(f"Failed to download {group}: {resp.status_code}")

    # Parse CSVs to find Sensex index and options
    global index_token, index_exch_seg, sensex_options
    for group in relevant_groups:
        try:
            with open(f"{group}.csv", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                print(f"Columns in {group}.csv:", reader.fieldnames)  # Print once for debugging/adjustment
                for row in reader:
                    ts = row.get('tradingSymbol', '') or ''
                    if 'SENSEX' not in ts:
                        continue

                    token = row.get('exchToken') or row.get('token') or row.get('scripCode', '')
                    exch_seg = row.get('exchange', 'BSE' if 'IDX' in ts else 'BFO')
                    instrument = row.get('instrumentType') or row.get('instrument', '')
                    option_type = row.get('optionType', '').strip()
                    strike_str = row.get('strikePrice', '').strip()
                    expiry_str = row.get('expiryDate', '').strip()

                    if instrument == 'INDEX' or (option_type == '' and strike_str in ['', '0']):
                        index_token = token
                        index_exch_seg = exch_seg
                        print(f"Found Sensex Index - Token: {token}_{exch_seg} (Symbol: {ts})")
                    else:
                        # Option contract
                        try:
                            strike = float(strike_str) if strike_str else 0.0
                            exp_date = datetime.strptime(expiry_str, "%Y-%m-%d").date() if expiry_str else date.max
                        except:
                            continue  # Skip malformed
                        sensex_options.append({
                            'token': token,
                            'exch_seg': exch_seg,
                            'strike': strike,
                            'option_type': option_type,
                            'expiry': exp_date
                        })
        except Exception as e:
            print(f"Error parsing {group}.csv: {e}")

    if not index_token:
        print("Sensex index token not found. Check CSVs and column names.")
        exit(1)

    if not sensex_options:
        print("No Sensex options found. Check CSVs.")

    # === WEBSOCKET STREAMING ===
    apikey = config.credentials['apikey']
    auth_token = f"{apikey}:{access_token}"
    global nx_stream
    nx_stream = NxtradStream("api.tradejini.com", stream_cb=stream_cb, connect_cb=connect_cb)
    nx_stream.connect(auth_token)

    # Keep script running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")
        nx_stream.disconnect()