"""Definition of code vector."""

from typing import Iterator, Sequence, Tuple

from sage.all import vector, GF


class Vector:
    """
    An implementation of code vectors used in the algorithm for efficient looping
    over the components.

    Each participant has a code :math:`c^i \\in GF(q)^{p_i}` where :math:`p_i` are the
    parameters assigned for each participant (:math:`1 \\leq i \\leq n`). The code
    vector is then :math:`c = (c^1, \\dots, c^n) \\in GF(q)^{p[P]}`.

    An iterator is defined on the code vector since we work with components :math:`c^i`.
    See the examples.

    Attributes
    ----------
    c : tuple or list or string
        A tuple or list or string of integers that contains the elements of a code vector.
    base_ring : GF
        The base ring of the code vector.
    pi : tuple
         The parameters assigned to the participant.

    Examples
    --------
    >>> parameters = (2, 3, 3, 2)
    >>> v = Vector([0, 1, 0, 1, 0, 1, 0, 1, 0, 1], GF(2), parameters)
    >>> for i in v:
    ...     print(i)
    (0, 1)
    (0, 1, 0)
    (1, 0, 1)
    (0, 1)
    >>> for i in Vector((1, 0, 1, 0, 1, 0, 1, 0, 1, 0), GF(2), parameters):
    ...     print(i)
    (1, 0)
    (1, 0, 1)
    (0, 1, 0)
    (1, 0)
    >>> for i in Vector("0110101011", GF(2), parameters):
    ...     print(i)
    (0, 1)
    (1, 0, 1)
    (0, 1, 0)
    (1, 1)

    """
    def __init__(self,
                 c: Sequence,
                 base_ring: GF,
                 pi: Tuple[int, ...]) -> None:
        self.c = vector(c, base_ring)
        self.base_ring = base_ring
        self.parameters = pi

    def is_zero(self) -> bool:
        """Returns ``True`` if the code vector is zero, ``False`` otherwise."""
        return self.c.is_zero()

    def __iter__(self) -> Iterator:
        i = 0
        for s in self.parameters:
            yield self.c[i:s+i]
            i += s

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return False
        return (self.base_ring == other.base_ring and
                self.c == other.c and
                self.parameters == other.parameters)

    def __ne__(self, other: "Vector") -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash((self.c + self.parameters))

    def __str__(self) -> str:
        return str(self.c)
