import unittest

from sage.all import GF, span, vector

from linearconstruction.code_description import *
from linearconstruction.codevector import Vector


class TestCodeDescription(unittest.TestCase):
    def setUp(self):
        self.v0 = Vector((0, 0, 0, 0, 0, 0, 0, 0), GF(2), (2, 2, 2, 2))
        self.v1 = Vector((0, 1, 0, 0, 1, 0, 0, 0), GF(2), (2, 2, 2, 2))
        self.v2 = Vector((1, 0, 1, 0, 1, 0, 1, 0), GF(2), (2, 2, 2, 2))

    def test_p_support(self):
        self.assertEqual(p_support(self.v0), set())
        self.assertEqual(p_support(self.v1), {1, 3})
        self.assertEqual(p_support(self.v2), {1, 2, 3, 4})

    def test_epsilon(self):
        self.assertEqual(epsilon(0, 1), [])
        self.assertEqual(epsilon(1, 0), [])
        self.assertEqual(epsilon(0, -1), [])
        self.assertEqual(epsilon(-1, 1), [])
        self.assertEqual(epsilon(1, 1), [(1, 1)])
        self.assertEqual(epsilon(3, 2), [(1, 1), (2, 1), (3, 1), (1, 2), (2, 2), (3, 2)])

    def test_jth_unit_vector(self):
        self.assertEqual(jth_unit_vector(1, 3, GF(2)), vector([1, 0, 0], GF(2)))
        self.assertEqual(jth_unit_vector(2, 3, GF(2)), vector([0, 1, 0], GF(2)))
        self.assertRaises(ValueError, jth_unit_vector, 0, 3, GF(2))
        self.assertRaises(ValueError, jth_unit_vector, 5, 3, GF(2))

    def test_projection(self):
        self.assertEqual(projection(self.v0, {2, 4}, (2, 2, 2, 2)), Vector((0, 0, 0, 0), GF(2), (2, 2)))
        self.assertEqual(projection(self.v1, {1, 2}, (2, 2, 2, 2)), Vector((0, 1, 0, 0), GF(2), (2, 2)))
        self.assertEqual(projection(self.v2, {1, 2, 3, 4}, (2, 2, 2, 2)), self.v2)
        self.assertRaises(ValueError, projection, self.v2, set(), (2, 2, 2, 2))

    def test_generate_label(self):
        gen_lab_1 = list(generate_label({1, 2, 3, 4}, (2, 3, 2, 3), {2, 3}, GF(2), []))
        expected = [Vector((0, 0, 0, 0, 0, 0, 1, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 0, 0, 0, 1, 0, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 0, 0, 0, 1, 1, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 0, 0, 1, 0, 0, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 0, 0, 1, 0, 1, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 0, 0, 1, 1, 0, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 0, 0, 1, 1, 1, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 0, 1, 0, 0, 0, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 0, 1, 0, 0, 1, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 0, 1, 0, 1, 0, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 0, 1, 0, 1, 1, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 0, 1, 1, 0, 0, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 0, 1, 1, 0, 1, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 0, 1, 1, 1, 0, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 0, 1, 1, 1, 1, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 0, 0, 0, 0, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 0, 0, 0, 1, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 0, 0, 1, 0, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 0, 0, 1, 1, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 0, 1, 0, 0, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 0, 1, 0, 1, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 0, 1, 1, 0, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 0, 1, 1, 1, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 1, 0, 0, 0, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 1, 0, 0, 1, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 1, 0, 1, 0, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 1, 0, 1, 1, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 1, 1, 0, 0, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 1, 1, 0, 1, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 1, 1, 1, 0, 0, 0, 0), GF(2), (2, 3, 2, 3)),
                    Vector((0, 0, 1, 1, 1, 1, 1, 0, 0, 0), GF(2), (2, 3, 2, 3))]
        self.assertEqual(gen_lab_1, expected)
        gen_lab_2 = list(generate_label({1, 2, 3, 4}, (2, 3, 2, 3), {2, 3}, GF(2),
                         span([vector([0, 1, 1, 0, 1, 0, 0, 0, 0, 0], GF(2)),
                               vector([0, 0, 0, 0, 0, 1, 0, 0, 1, 0])], GF(2))))
        self.assertEqual(gen_lab_2, expected)


if __name__ == "__main__":
    unittest.main()
