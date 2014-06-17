enabled = False


def get_parental_enabled():
    return enabled


def set_parental_enabled(setting):
    global enabled
    enabled = setting
