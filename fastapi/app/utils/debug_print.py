import inspect

def debug_print(message=''):
    frame = inspect.currentframe().f_back
    func_name = frame.f_code.co_name
    args = frame.f_locals

    print(f'{func_name} | args={args}: {message}')