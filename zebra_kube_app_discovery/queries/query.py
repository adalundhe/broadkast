import uvloop
uvloop.install()
from typing import List, Optional
from .selector import Selector


class Query:

    def __init__(self, labels: Optional[List[dict]]=None, fields: Optional[List[dict]]=None) -> None:
        self.labels = labels
        self.fields = fields

        if labels:
            self.labels = [ Selector(selector) for selector in labels ]

        if fields:
            self.fields = [ Selector(selector) for selector in fields ]

        self.field_selectors = None
        self.label_selectors = None

    async def to_selectors(self) -> None:  

        if self.labels:        
            self.label_selectors = ','.join([
                f'{selector.name}{selector.operator}{selector.value}' for selector in self.labels
            ])

        if self.fields:
            self.field_selectors = ','.join([
                f'{selector.name}{selector.operator}{selector.value}' for selector in self.fields
            ])
