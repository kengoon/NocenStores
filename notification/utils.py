from plyer.utils import Proxy
from plyer.utils import Platform

platform = Platform()


class Proxi(Proxy):
    def _ensure_obj(self):
        obj = object.__getattribute__(self, '_obj')
        if obj:
            return obj
        # do the import
        try:
            # name = object.__getattribute__(self, '_name')
            module = "notification.android_notification"
            mod = __import__(module, fromlist='.')
            obj = mod.instance()
        except Exception:
            import traceback
            traceback.print_exc()
            facade = object.__getattribute__(self, '_facade')
            obj = facade()

        object.__setattr__(self, '_obj', obj)
        return obj
