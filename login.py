# -*- coding: utf-8 -*-

import base64
import models.error as error
import hashlib
import sys
from util.webclient import WebClient
from models import session

host = "https://sb-talk.kakao.com"


def hash_uuid(uuid):
    sha256 = hashlib.sha256(uuid).digest()
    sha1 = hashlib.sha1(uuid).digest()
    return base64.b64encode(sha1 + sha256)


def try_login(email, password, uuid):
    ua = "KT/2.2.4 Mc/10.12.3 ko"

    wc = WebClient(host)
    wc.add_header("User-Agent", ua)
    wc.add_header("Accept-Language", "ko")
    wc.add_header("A", "mac/2.2.4/ko")

    uuid = hash_uuid(uuid)
    xvc = "|".join(["HSOJ", email, uuid, "RABOOF", ua])
    wc.add_header("X-VC", hashlib.sha512(xvc).hexdigest()[:16])

    login_result = wc.post("/mac/account/login.json", email=email, password=password, device_uuid=uuid, name="zion_MBP")

    if login_result["status"] != 0:
        print error.lookup_error(login_result["status"])
        return None

    wc.add_header("S", "{0}-{1}".format(login_result["sessionKey"].decode("ascii"), uuid))

    sess = session.Session(wc, login_result["userId"], login_result["accountId"], login_result["sessionKey"], uuid)
    return sess
