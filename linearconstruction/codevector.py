"""Definition of code vector."""

from typing import Iterator, List, Sequence, Tuple

from sage.all import vector, GF

__all__ = ["Vector"]


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

    @classmethod
    def from_vector(cls, v: vector, pi: Tuple[int, ...]) -> "Vector":
        """
        Create a ``Vector`` from a Sage *vector*.

        Parameters
        ----------
        v : Sage.vector
            A Sage vector
        pi : tuple
            The parameters of all participants.

        Returns
        -------
        vec : Vector

        """
        return cls(v.list(), v.base_ring(), pi)

    @classmethod
    def all_zero(cls, base_ring: GF, pi: Tuple[int, ...]) -> "Vector":
        """
        Create an all-zero vector in *base_ring* of size *pi*.

        Parameters
        ----------
        base_ring : GF
            The base ring in which the vector is defined.
        pi : tuple
            The parameters of all participants.

        Returns
        -------
        v : Vector
            The all-zero vector.

        Examples
        --------
        >>> v = Vector.all_zero(GF(2), (2, 3, 3, 2))
        >>> for i in v:
        ...     print(i)
        (0, 0)
        (0, 0, 0)
        (0, 0, 0)
        (0, 0)

        """
        return cls([0] * sum(pi), base_ring, pi)

    def is_zero(self) -> bool:
        """Returns ``True`` if the code vector is zero, ``False`` otherwise."""
        return self.c.is_zero()

    def list(self) -> List[int]:
        """Return a list of elements of ``self``."""
        return self.c.list()

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

    def __mul__(self, other) -> "Vector":
        v = self.c * other
        return Vector.from_vector(v, self.parameters)

    def __rmul__(self, other) -> "Vector":
        v = other * self.c
        return Vector.from_vector(v, self.parameters)

    def __hash__(self) -> int:
        return hash((self.c + self.parameters))

    def __str__(self) -> str:
        return str(self.c)
