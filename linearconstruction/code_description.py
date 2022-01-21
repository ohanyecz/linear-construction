from itertools import chain, product
from typing import Iterable, Iterator, List, Set, Tuple

from sage.all import vector, GF, span

from .codevector import Vector

__all__ = ["p_support", "epsilon", "jth_unit_vector", "projection", "generate_label"]


def p_support(v: Vector) -> Set[int]:
    """
    Calculate the p-support of a code vector *v*.

    Let :math:`\\mathbf{c}^i \\in \\text{GF}(q)^{p_i}`, :math:`1 \\leq i \\leq n` and
    :math:`\\mathbf{c} = (\\mathbf{c}^1, \\dots, \\mathbf{c}^n) \\in \\text{GF}(q)^{p[\\mathcal{P}]}`.
    The p-support of a vector :math:`\\mathbf{c}` is defined as the set of coordinates,
    :math:`i`, :math:`(1 \\leq i \\leq n)`, for which :math:`\\mathbf{c}^i \\ne \\mathbf{0}`:

    .. math::
        \\text{sup}_p(\\mathbf{c}) = \\{ i : \\mathbf{c}^i \\ne \\mathbf{0} \\}

    Parameters
    ----------
    v : `~linearconstruction.codevector.Vector`
        The code vector whose p-support is calculated.

    Returns
    -------
    res : set
        The set of coordinates for which :math:`\\mathbf{c}^i \\ne \\mathbf{0}`.

        .. note::
            The set of coordinates are indexed from 1 instead of 0!

    Examples
    --------
    >>> finite_field = GF(2)
    >>> v = Vector((1, 0, 0, 1, 0, 0, 0, 1, 0, 0), finite_field, (2, 3, 3, 2))
    >>> p_support(v)
    {1, 2, 3}
    >>> v = Vector((0, 0, 0, 0, 0, 0, 0, 0, 0, 0), finite_field, (2, 3, 3, 2))
    >>> p_support(v)
    set()

    """
    return {i for i, cw in enumerate(v, start=1) if any(cw)}


def epsilon(r: int, k: int) -> List[Tuple[int, int]]:
    """
    Returns a list of pairs :math:`(i,j)`, where :math:`1 \\leq i \\leq r, 1 \\leq j \\leq k`.

    Parameters
    ----------
    r : int
        The number of sets in the minimal sets in Gamma.
    k : int
        The size of the secret.

    Returns
    -------
    res : list
        The list of pairs. If either of the parameters less than or equal to zero, an empty list is returned.

    Examples
    --------
    >>> epsilon(3, 2)
    [(1, 1), (2, 1), (3, 1), (1, 2), (2, 2), (3, 2)]

    """
    return [(i, j) for j in range(1, k+1) for i in range(1, r+1)]


def jth_unit_vector(j: int, dim: int, base_ring: GF) -> vector:
    """
    Creates the *j*'th unit vector of *dim* in *base_ring*.

    Parameters
    ----------
    j : int
        Specifies which component of the unit vector equals to 1.
    dim : int
        The dimension of the unit vector.
    base_ring : GF
        The base ring in which the unit vector is defined.

    Returns
    -------
    v : vector
        A Sage vector containing the j'th unit vector.

    Raises
    ------
    ValueError
        If either *j* is bigger than the *dim* of vector or *j* equals to 0.

    Examples
    --------
    >>> jth_unit_vector(1, 3, GF(2))
    (1, 0, 0)
    >>> jth_unit_vector(3, 3, GF(2))
    (0, 0, 1)

    """
    if j > dim:
        raise ValueError(f"'j' is bigger than 'dim' ({j} > {dim})")
    if j == 0:
        raise ValueError(f"Cannot create 0th unit vector.")
    e = [0] * dim
    e[j - 1] = 1
    return vector(e, base_ring)


def projection(v: Vector, x: Iterable, pi: Tuple[int, ...]) -> Vector:
    """
    Calculates the projection of code vector *v* on set of participants *x*.

    Let :math:`\\mathbf{c}^i \\in \\text{GF}(q)^{p_i}`, :math:`1 \\leq i \\leq n` and
    :math:`\\mathbf{c} = (\\mathbf{c}^1, \\dots, \\mathbf{c}^n) \\in \\text{GF}(q)^{p[\\mathcal{P}]}`.
    Let :math:`X = \\{ i_1, \\dots, i_m \\} \\subseteq \\{ 1, \\dots, n \\}`, with
    :math:`i_1 < \\dots < i_m`. Then the projection of vector :math:`\\mathbf{c}`
    on :math:`X` is defined as

    .. math::

        \\mathbf{c}_X = (\\mathbf{c}^{i_1}, \\dots, \\mathbf{c}^{i_m}).

    Notice that :math:`\\mathbf{c} = \\mathbf{c}_{\\mathcal{P}}`.

    Parameters
    ----------
    v : `~linearconstruction.codevector.Vector`
        The code vector whose projection should be calculated.
    x : set
        The set of participants taking the projection on.
    pi : tuple
        The parameters of all participants. The projection vector will contain
        parameters of participants in *x*.

    Returns
    -------
    v : `~linearconstruction.codevector.Vector`
        The projection of *v* on *x*.

    Examples
    --------
    >>> parameters = (2, 3, 3, 2)
    >>> v = Vector((0, 1, 0, 1, 0, 1, 0, 1, 1, 1), GF(2), parameters)
    >>> p = projection(v, [1, 3], parameters)
    >>> for i in p:
    ...     print(i)
    (0, 1)
    (1, 0, 1)
    >>> p = projection(v, [1, 2, 3, 4], parameters)
    >>> for i in p:
    ...     print(i)
    (0, 1)
    (0, 1, 0)
    (1, 0, 1)
    (1, 1)
    >>> p == v
    True

    """
    if not x:
        raise ValueError(f"Cannot create a projection on an empty set 'x'.")
    x = sorted(x)
    res = []
    for i, c in enumerate(v, start=1):
        if i in x:
            res += c
    pi_x = tuple(pi[i - 1] for i in x)
    return Vector(res, v.base_ring, pi_x)


def generate_label(participants: set,
                   pi: Tuple[int, ...],
                   x_i: Iterable,
                   base_ring: GF,
                   lin_span: span) -> Iterator[Vector]:
    """
    Make an iterator over the possible edge labels.

    An edge is labeled with a set of vectors :math:`S \\in \\text{GF}(q)^{p[P]}` having the
    property that for all :math:`\\mathbf{c} \\in S`

    .. math::

        \\sup(\\mathbf{c}) \\subseteq X_{i_{m + 1}}

    where :math:`0 \\leq m < s` are the levels of the search tree.

    Parameters
    ----------
    participants : set
        The participants in the secret sharing scheme.
    pi : tuple
        The parameters of all participants.
    x_i : set
        A node of the search tree to which the edge goes.
    base_ring : GF
        The ring in which the labels are defined.
    lin_span : span
        The linear span of the vectors up until this node.

    Returns
    -------
    it : Iterator
        An iterator on `~linearconstruction.codevector.Vector` over the possible edge labels.
    """
    parts = []
    for p in participants:
        if p in x_i:
            parts.append(product(base_ring.list(), repeat=pi[p - 1]))
        else:
            parts.append([tuple([0] * pi[p - 1])])

    for p in product(*parts):
        vec = list(chain.from_iterable(p))
        if vec != [0] * sum(pi) and vec not in lin_span:
            yield Vector(vec, base_ring, pi)
