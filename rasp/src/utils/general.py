import datetime
import sys
import threading

import pytz

import time



def run_server_on_thread(target_fun, *args, **kwargs):
    original_stdout = sys.stdout

    def target_fun_with_redirected_stdout(*args, **kwargs):
        sys.stdout = original_stdout
        try:
            target_fun(*args, **kwargs)
        finally:
            sys.stdout = sys.__stdout__

    proc = threading.Thread(target=target_fun_with_redirected_stdout, args=args, kwargs=kwargs)
    proc.start()
    return proc


def milis_to_utc_datetime(raw_milis: int):
    seconds, milis = divmod(raw_milis, 1000)
    epoch = datetime.datetime.fromtimestamp(seconds, tz=pytz.utc)
    epoch = epoch.replace(microsecond=int(milis * 1000))
    return epoch


def now_utc_datetime():
    return datetime.datetime.now(tz=pytz.utc)


def diff_to_now_utc_timestamp(raw_milis: int):
    milis_dt = milis_to_utc_datetime(raw_milis)
    now_dt = now_utc_datetime()
    diff = now_dt - milis_dt
    # convert difference to milliseconds
    return diff.total_seconds()


def milis_to_utc_timestamp(raw_milis: int):
    epoch = milis_to_utc_datetime(raw_milis)
    return epoch.timestamp()


def now_utc_timestamp():
    return now_utc_datetime().timestamp()
