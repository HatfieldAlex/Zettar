from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Callable, Optional

class Header:
    def __init__(self, extract: str, clean: Callable[[str], str]):
        self.extract = extract
        self.clean = clean


class Dataset:
    def __init__(self, url: str, identifier: str, headers: list[Header]):
        self.url = url
        self.identifier = identifier
        self.headers = headers

class ConnectionApplication:
    def __init__(self, dataset: Dataset):
        self.dataset = dataset

class Substation:
    def __init__(self, dataset: Dataset):
        self.dataset = dataset

class DNO:
    def __init__(self, name: str, substation: Substation, connection_application: ConnectionApplication):
        self.name = name
        self.substation = substation
        self.connection_application = connection_application 


