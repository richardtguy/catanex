from flask import make_response
from functools import wraps, update_wrapper


def nocache(view):
    @wraps(view)
    def no_cache(*args, **kwargs):
        response = make_response(view(*args, **kwargs))
        response.cache_control.no_cache = True
        return response
        
    return update_wrapper(no_cache, view)