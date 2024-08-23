import unittest

from fastapi import FastAPI
from starlette.requests import Request

from app.stats import StatsdMiddleware


class TestApi(unittest.TestCase):

    def test_normalize_path(self) -> None:
        app = FastAPI()
        mw = StatsdMiddleware(app, "test")

        req = self.create_req("/foo/bar")
        assert mw.normalize_path(req) == "/foo/bar"

        req = self.create_req("/resource/patient/_search")
        assert mw.normalize_path(req) == "/resource/patient/_search"

        req = self.create_req("/resource/patient/1234")
        assert mw.normalize_path(req) == "/resource/patient/%resource_id%"

        req = self.create_req("/resource/patient/1234/_history/5678")
        assert mw.normalize_path(req) == "/resource/patient/%resource_id%/_history/%version_id%"

        req = self.create_req("/resource/foobar/1234/_history/5678")
        assert mw.normalize_path(req) == "/resource/foobar/%resource_id%/_history/%version_id%"


    def create_req(self, path: str) -> Request:
        return Request(
            scope={
                'type': 'http',
                'scheme': 'http',
                'method': 'PUT',
                'path': path,
                'query_string': b'',
                'headers': {}
            },
        )
