from cachetools import TTLCache
from functools import wraps

customers_cache = TTLCache(maxsize=1000, ttl=600)
all_customers_cache = TTLCache(maxsize=100, ttl=600)

def cache_evict(*cache_names):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            for cache_name in cache_names:
                if cache_name == "customers":
                    customers_cache.clear()
                    print("Кэш customers очищен")
                elif cache_name == "allCustomers":
                    all_customers_cache.clear()
                    print("Кэш allCustomers очищен")
            return result
        return wrapper
    return decorator