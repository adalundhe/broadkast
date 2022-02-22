from typing import Optional


class Selector:

    def __init__(self, selector: dict) -> None:
        self.name = selector.get('name')
        self.operator = selector.get('operator', '=')
        self.value = selector.get('value')

    def to_dict(self):
        return {
            'name': self.name,
            'operator': self.operator,
            'value': self.value
        }