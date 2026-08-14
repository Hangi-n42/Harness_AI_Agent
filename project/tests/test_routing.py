"""test_routing.py — the rule-based router picks the right skill."""

from __future__ import annotations

import unittest

from helpers import FakeLLM
from runtime import Runtime


class RoutingTest(unittest.TestCase):
    def setUp(self):
        self.rt = Runtime(llm=FakeLLM())

    def test_route_campus(self):
        self.assertEqual(self.rt.route("深圳大学的校训是什么？").name, "campus")

    def test_route_library(self):
        self.assertEqual(self.rt.route("图书馆在哪个校区？").name, "library")

    def test_route_translation(self):
        self.assertEqual(self.rt.route("请把这段话翻译成英文").name, "translation")

    def test_route_fallback_out_of_scope(self):
        self.assertEqual(self.rt.route("今天天气怎么样？").name, "fallback")

    def test_route_library_before_campus(self):
        # "深圳大学" + "图书馆" both present -> the more specific skill wins.
        self.assertEqual(self.rt.route("深圳大学图书馆在哪里").name, "library")


if __name__ == "__main__":
    unittest.main()
