import unittest

from sage.all import powerset

from linearconstruction import AccessStructure


class TestAccessStructure(unittest.TestCase):
    def setUp(self):
        self.ac1 = AccessStructure(4, {1: {"a", "b"}, 2: {"c", "d"}, 3: {"b", "c"}})
        self.ac2 = AccessStructure(4, {1: {"a", "b", "c", "d"}})
        self.ac3 = AccessStructure(4, {1: set()})
        self.ac4 = AccessStructure(4, {1: {"c", "d"}, 2: {"a", "b"}, 3: {"b", "c"}})
        self.ac5 = AccessStructure(5, {1: {"a", "b"}, 2: {"a", "c"}, 3: {"a", "d"}, 4: {"a", "e"}, 5: {"b", "c", "d", "e"}})  # self-dual

    def test_constructor(self):
        self.assertEqual({1, 2, 3, 4}, self.ac1.participants)
        self.assertEqual(len(self.ac1.delta_max.keys()), 3)
        self.assertEqual({frozenset(i) for i in self.ac1.gamma_min.values()}, {frozenset({3, 4}), frozenset({2, 3}), frozenset({1, 2})})
        self.assertEqual({frozenset(i) for i in self.ac1.delta_max.values()}, {frozenset({2, 4}), frozenset({1, 4}), frozenset({1, 3})})

        for ac in [self.ac1, self.ac2, self.ac3]:
            with self.subTest(ac=ac):
                self.assertEqual({frozenset(i) for i in ac.gamma} | {frozenset(i) for i in ac.delta}, {frozenset(i) for i in powerset(ac.participants)})

    def test_from_args_constructor(self):
        ac1 = AccessStructure.from_args(4, "ab", "cd", "bc")
        ac2 = AccessStructure.from_args(4, "ab", "cd", "bc", create_dual=True)
        self.assertEqual({frozenset(i) for i in ac1.gamma_min.values()}, {frozenset({1, 2}), frozenset({3, 4}), frozenset({2, 3})})
        self.assertEqual({frozenset(i) for i in ac1.delta_max.values()}, {frozenset({1, 3}), frozenset({1, 4}), frozenset({2, 4})})

        self.assertEqual({frozenset(i) for i in ac2.gamma_min.values()}, {frozenset({1, 3}), frozenset({2, 3}), frozenset({2, 4})})
        self.assertEqual({frozenset(i) for i in ac2.delta_max.values()}, {frozenset({1, 2}), frozenset({1, 4}), frozenset({3, 4})})

    def test_from_iterable_constructor(self):
        ac1 = AccessStructure.from_iterable(4, ["ab", "cd", "bc"])
        ac2 = AccessStructure.from_iterable(4, ["ab", "cd", "bc"], create_dual=True)
        self.assertEqual({frozenset(i) for i in ac1.gamma_min.values()}, {frozenset({1, 2}), frozenset({3, 4}), frozenset({2, 3})})
        self.assertEqual({frozenset(i) for i in ac1.delta_max.values()}, {frozenset({1, 3}), frozenset({1, 4}), frozenset({2, 4})})

        self.assertEqual({frozenset(i) for i in ac2.gamma_min.values()}, {frozenset({1, 3}), frozenset({2, 3}), frozenset({2, 4})})
        self.assertEqual({frozenset(i) for i in ac2.delta_max.values()}, {frozenset({1, 2}), frozenset({1, 4}), frozenset({3, 4})})

    def test_dual(self):
        for ac in [self.ac1, self.ac2, self.ac3, self.ac4]:
            with self.subTest(ac=ac):
                dual = ac.dual()
                self.assertEqual({1, 2, 3, 4}, dual.participants)
                self.assertEqual({frozenset(i) for i in dual.gamma} | {frozenset(i) for i in dual.delta}, {frozenset(i) for i in powerset(dual.participants)})

        dual = self.ac5.dual()
        self.assertEqual({1, 2, 3, 4, 5}, dual.participants)
        self.assertEqual({frozenset(i) for i in dual.gamma} | {frozenset(i) for i in dual.delta}, {frozenset(i) for i in powerset(dual.participants)})

    def test_access_structure_equality(self):
        self.assertEqual(self.ac1, self.ac1)
        self.assertEqual(self.ac1, self.ac4)
        self.assertEqual(self.ac4, self.ac1)

    def test_access_structure_inequality(self):
        self.assertNotEqual(self.ac1, self.ac2)
        self.assertNotEqual(self.ac2, self.ac1)


if __name__ == "__main__":
    unittest.main()
