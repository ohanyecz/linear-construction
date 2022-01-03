"""Implementation of access structure on a set of participants."""

from string import ascii_lowercase
from typing import Iterable

from sage.all import powerset

from .typing import QualifiedSets

__all__ = ["AccessStructure"]


class AccessStructure:
    """Implementation of an access structure on a set of participants.

    An access structure :math:`(\\Gamma, \\Delta)` on the set of participants specifies those
    subsets of the participants who are qualified to reconstruct the secret and those subsets
    of the participants who are forbidden to obtain additional knowledge about the secret by
    pooling their shares.

    An access structure is complete if :math:`\\Gamma \\cup \\Delta = 2^P`. The current
    implementation assumes complete access structures.


    Attributes
    ----------
    n : int
        The number of participants in the secret sharing scheme
    gamma_min : dict
        A dictionary of the minimal qualified sets.


    Examples
    --------
    >>> ac = AccessStructure(4, {1: {"a", "b"}, 2: {"c", "d"}, 3: {"b", "c"}})
    >>> ac.gamma_min
    {1: {'a', 'b'}, 2: {'d', 'c'}, 3: {'b', 'c'}}

    """
    def __init__(self,
                 n: int,
                 gamma_min: QualifiedSets) -> None:
        self.participants = {i for i in ascii_lowercase[:n]}
        self.gamma_min = gamma_min
        self.gamma, self.delta = _calculate_sets(self.participants, gamma_min)
        self.delta_max = _calculate_group(max, self.delta)

    @classmethod
    def from_args(cls, n: int, *iterables: Iterable) -> "AccessStructure":
        """Create a non-trivial access structure form ``*iterables``.


        Returns
        -------
        ac : AccessStructure


        Examples
        --------
        >>> ac = AccessStructure.from_args(4, "ab", "cd", "bc")
        >>> ac.gamma_min
        {1: {'b', 'a'}, 2: {'c', 'd'}, 3: {'c', 'b'}}

        """
        gamma_min = {k: set(v) for k, v in enumerate(iterables, start=1)}
        return cls(n, gamma_min)

    @classmethod
    def from_iterable(cls, n: int, iterable: Iterable) -> "AccessStructure":
        """Create a non-trivial access structure from ``iterable``.


        Returns
        -------
        ac : AccessStructure


        Examples
        --------
        >>> ac = AccessStructure.from_iterable(4, [["a", "b"], ["c", "d"], ["b", "c"]])
        >>> ac.gamma_min
        {1: {'a', 'b'}, 2: {'d', 'c'}, 3: {'b', 'c'}}
        >>> ac = AccessStructure.from_iterable(4, [{"a", "b"}, {"b", "c"}, {"c", "d"}])
        >>> ac.gamma_min
        {1: {'b', 'a'}, 2: {'b', 'c'}, 3: {'c', 'd'}}

        """
        return cls(n, {k: set(v) for k, v in enumerate(iterable, start=1)})

    def dual(self) -> "AccessStructure":
        """Calculate the dual access structure of ``self``.

        The dual :math:`(\\Gamma^{\\bot}, \\Delta^{\\bot})` of :math:`(\\Gamma, \\Delta)` is defined by

        .. math::

            \\{ X : X^c \\in \\Delta \\} = \\Gamma^{\\bot},
            \\{ X : X^c \\in \\Gamma \\} = \\Delta^{\\bot}

        where :math:`X^c` is the complement of a subset of participants: :math:`X \\subseteq \\mathcal{P}`.


        Returns
        -------
        ac : AccessStructure
            The dual access structure of ``self``.


        Examples
        --------
        >>> ac = AccessStructure(4, {1: {"a", "b"}, 2: {"c", "d"}, 3: {"b", "c"}})
        >>> ac.dual().gamma_min
        {1: {'d', 'b'}, 2: {'a', 'd'}, 3: {'a', 'c'}}

        """
        gamma_min_dual = {}

        k = 1
        for x in powerset(self.participants):
            x = set(x)
            if self.participants - x in self.delta_max.values():
                gamma_min_dual[k] = x
                k += 1
        n = len(self.participants)
        return AccessStructure(n, gamma_min_dual)

    def __eq__(self, other) -> bool:
        if not isinstance(other, AccessStructure):
            return False
        return (self.participants == other.participants and
                len(self.gamma_min) == len(other.gamma_min) and
                all(i in other.gamma_min.values() for i in self.gamma_min.values()) and
                all(i in self.gamma_min.values() for i in other.gamma_min.values()) and
                len(self.delta_max) == len(other.delta_max) and
                all(i in other.delta_max.values() for i in self.delta_max.values()) and
                all(i in self.delta_max.values() for i in other.delta_max.values()))

    def __ne__(self, other) -> bool:
        return not self == other

    def __str__(self) -> str:
        return f"A non-trivial complete access structure on the set of {len(self.participants)} participants."


def _calculate_group(f, groups):
    temp = set(frozenset(i) for i in groups)
    res = {}
    k = 1
    while temp:
        s = {i for i in temp if len(i) == f(len(j) for j in temp)}
        for v in s:
            res[k] = set(v)
            k += 1
        temp = temp - s - {i for i in temp if any(i <= j for j in s)}
    return res


def _calculate_sets(participants, gamma_min):
    gamma, delta = [], []
    for s in powerset(participants):
        s = set(s)
        if any(i <= s for i in gamma_min.values()):
            gamma.append(s)
        else:
            delta.append(s)
    return gamma, delta
