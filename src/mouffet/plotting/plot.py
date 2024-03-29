from importlib import import_module
import sys


class Plot:

    DEFAULT_PLOTTING_PACKAGE = "mouffet.plotting.plotnine"

    def __init__(self) -> None:
        self.pkg = None

    def set_plotting_package(self, pkg=None, options=None):
        if not pkg:
            if options is None:
                options = {}
            pkg = options.get("plotting_package", self.DEFAULT_PLOTTING_PACKAGE)
        try:
            self.pkg = import_module(pkg)
        except ImportError:
            print("Error! Package {} was not found".format(pkg))

    def __getattr__(self, name):
        if not name.startswith("__"):
            if self.pkg is None:
                print("setting default plotting method")
                self.set_plotting_package()
            return getattr(self.pkg, name)
        return getattr(super(), name)


sys.modules[__name__] = Plot()


# def call_function(func_name, *args, **kwargs):
#     global plotting_pkg
#     if not plotting_pkg:
#         set_plotting_method()
#     getattr(plotting_pkg, func_name)(*args, **kwargs)


# def import_package(options):
#     try:
#         method = "plot." + options.get("plotting_method", DEFAULT_PLOTTING_PACKAGE)
#         pkg = import_module(method)
#     except ImportError:
#         print("Error! Package {} was not found".format(method))
#     return pkg


# def plot_PR_curve(*args, **kwargs):
#     # pkg = import_package(options)
#     # return getattr(pkg, "plot_PR_curve")(results, options)
#     call_function("plot_PR_curve", *args, **kwargs)


# def save_as_pdf(*args, **kwargs):
#     # pkg = import_package(options)
#     # return getattr(pkg, "plot_PR_curve")(results, options)
#     call_function("save_as_pdf", *args, **kwargs)
