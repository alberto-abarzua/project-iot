import sys
import threading

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