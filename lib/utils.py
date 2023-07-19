import inspect
from datetime import datetime

def format_time(timestamp):
    if type(timestamp) == str:
        dt = datetime.fromisoformat(timestamp)
        return dt.strftime("%Y-%m-%d %H:%M")
    return timestamp.strftime("%Y-%m-%d %H:%M")

def get_function_arity(func):
    return len(inspect.getfullargspec(func).args)

def get_function_arity_range(func):
    sig = inspect.signature(func)
    required = 0
    optional = 0
    for param in sig.parameters.values():
        if param.default is param.empty:
            required += 1
        else:
            optional += 1

    return [required, required + optional]
