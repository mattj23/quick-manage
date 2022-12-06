import pytest
from quick_manage import IKeyStore
import quick_manage.s3


def test_basic_api():
    results = [cls.__name__ for cls in IKeyStore.__subclasses__()]
