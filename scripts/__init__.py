# __all__ = []
#
# import pkgutil
# import inspect
#
# for loader, name, is_pkg in pkgutil.walk_packages(__path__):
#     module = loader.find_module(name).load_module(name)
#
#     for name, value in inspect.getmembers(module):
#         if name.startswith('__'):
#             continue
#
#         globals()[name] = value
#         __all__.append(name)

from os.path import dirname, basename, isfile
import glob
modules = glob.glob(dirname(__file__)+"/*.py")
__all__ = [ basename(f)[:-3] for f in modules if isfile(f)]
