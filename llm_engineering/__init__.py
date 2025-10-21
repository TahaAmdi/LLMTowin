all = ["application", "domain", "infrastructure", "Settings"]

def __getattr__(name):
    if name == "Settings":
        from .settings import Settings
        return Settings
    elif name in ("application", "domain", "infrastructure"):
        from importlib import import_module
        return import_module(f"llm_engineering.{name}")
    raise AttributeError(name)