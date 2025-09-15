_state = {"value": "default"}


def set_value(new_value: str):
    _state["value"] = new_value


def get_state():
    return _state.copy()
