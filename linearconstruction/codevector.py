"""Definition of code vector."""

from dataclasses import dataclass
from typing import Iterator, Tuple

from sage.all import vector


@dataclass(frozen=True)
class Vector:
    """
    An implementation of code vectors used in the algorithm for efficient looping
    over the components.

    Each participant has a code :math:`c^i \\in GF(q)^{p_i}` where :math:`p_i` are the
    parameters assigned for each participant (:math:`1 \\leq i \\leq n`). The code
    vector is then :math:`c = (c^1, \\dots, c^n)` \\in GF(q)^{p[P]}`.

    An iterator is defined on the code vector since we work with components :math:`c^i`.
    See the examples.

    Attributes
    ----------
    c : vector
        A Sage vector holding the code vector.
    parameters : tuple
         The parameters assigned to the participant.

    Examples
    --------
    >>> parameters = (2, 3, 3, 2)
    >>> v = Vector(vector([0, 1, 0, 1, 0, 1, 0, 1, 0, 1]), parameters)
    >>> for i in v:
    ...     print(i)
    (0, 1)
    (0, 1, 0)
    (1, 0, 1)
    (0, 1)

    """
    c: vector
    parameters: Tuple[int, ...]

    def is_zero(self) -> bool:
        """Returns ``True`` if the code vector is zero, ``False`` otherwise."""
        return self.c.is_zero()

    def __iter__(self) -> Iterator:
        i = 0
        for s in self.parameters:
            yield self.c[i:s+i]
            i += s

    def __ne__(self, other: "Vector") -> bool:
        return not self == other

    def __hash__(self) -> int:
        return hash((self.c + self.parameters))
