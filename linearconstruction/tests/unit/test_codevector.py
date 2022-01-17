import unittest

from sage.all import GF, vector

from linearconstruction import Vector


class TestCodevector(unittest.TestCase):
    def test_constructor(self):
        v = Vector((0, 1, 0, 1, 0, 1, 0, 1, 0, 1), GF(2), (2, 3, 3, 2))
        self.assertEqual(v.c.base_ring(), GF(2))
        self.assertEqual(v.c, vector([0, 1, 0, 1, 0, 1, 0, 1, 0, 1]))

    def test_from_vector_constructor(self):
        v = vector([0, 1, 2, 1, 0, 1, 2, 0, 1, 2], GF(3))
        vec = Vector.from_vector(v, (2, 3, 3, 2))
        self.assertEqual(vec.base_ring, GF(3))
        self.assertEqual(vec.c, v)
        self.assertEqual(vec.parameters, (2, 3, 3, 2))

    def test_all_zero_constructor(self):
        v = Vector.all_zero(GF(3), (2, 3, 3, 2))
        self.assertEqual(v.c, vector([0] * 10, GF(3)))
        self.assertEqual(v.base_ring, GF(3))

    def test_is_zero(self):
        v1 = Vector([0, 0, 0, 0, 0, 0], GF(2), (2, 2, 2))
        v2 = Vector([0, 1, 2, 1, 0, 1], GF(3), (2, 2, 2))
        self.assertTrue(v1.is_zero())
        self.assertFalse(v2.is_zero())

    def test_iterator(self):
        v = Vector([0, 1, 2, 1, 0, 1, 2, 1, 0, 1], GF(3), (2, 3, 3, 2))
        it = iter(v)
        self.assertEqual(next(it), vector([0, 1], GF(3)))
        self.assertEqual(next(it), vector([2, 1, 0], GF(3)))
        self.assertEqual(next(it), vector([1, 2, 1], GF(3)))
        self.assertEqual(next(it), vector([0, 1], GF(3)))
        self.assertRaises(StopIteration, next, it)

    def test_equality(self):
        v1 = Vector([0, 1, 2, 1, 0], GF(3), (2, 3))
        self.assertEqual(v1, v1)

    def test_inequality(self):
        v1 = Vector([0, 1, 2, 1, 0], GF(3), (2, 3))
        v2 = Vector([0, 1, 2, 1, 0], GF(4), (2, 3))
        v3 = Vector([0, 1, 2, 1, 0], GF(3), (3, 2))
        v4 = "Hello"
        self.assertNotEqual(v1, v2)
        self.assertNotEqual(v2, v1)
        self.assertNotEqual(v1, v3)
        self.assertNotEqual(v3, v1)
        self.assertNotEqual(v2, v3)
        self.assertNotEqual(v3, v2)
        self.assertNotEqual(v1, v4)
        self.assertNotEqual(v4, v1)


if __name__ == "__main__":
    unittest.main()
