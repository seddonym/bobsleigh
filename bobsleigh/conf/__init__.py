from importlib import import_module


def get_settings_handler():
    """Detects and returns the settings handler for this installation."""
    # Import the installations - we need to do it using importlib
    # as otherwise it imports the settings package within this package
    installations = import_module('settings.installations')
    for handler in installations.INSTALLATIONS:
        if handler.is_current():
            return handler
    raise Exception("Could not detect a suitable settings handler " \
                    "for this installation.")

handler = get_settings_handler()
