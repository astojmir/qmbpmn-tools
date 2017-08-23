"""A useful profiling decorator."""
import cProfile as profile

def profiled(path):
    """A useful profiling decorator."""
    def _decorator(func):
        def _newfunc(*args, **kwargs):
            profiler = profile.Profile()
            ret = profiler.runcall(func, *args, **kwargs)
            profiler.dump_stats(path)
            return ret
        # Be well-behaved
        _newfunc.__name__ = func.__name__
        _newfunc.__doc__ = func.__doc__
        _newfunc.__dict__.update(func.__dict__)
        return _newfunc
    return _decorator
