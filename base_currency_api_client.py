from abc import ABC, abstractmethod


class BaseCurrencyAPIClient(ABC):
    def __init__(self, base_url: str):
        self.base_url = base_url

    @abstractmethod
    def date_injector(self, date_str: str) -> str:
        pass