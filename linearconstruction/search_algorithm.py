from copy import deepcopy
from itertools import product
from multiprocessing import Event, Value  # import only for typing
from queue import Queue  # import only for typing
import random
from typing import Dict, List, Union, Tuple, Set

from sage.all import GF, inverse_mod, matrix, span, vector

from .access_structure import AccessStructure
from .code_description import generate_label, jth_unit_vector, p_support, projection
from .codevector import Vector
from .typing import Epsilon

__all__ = ["SearchAlgorithm"]


class SearchAlgorithm:
    """
    The implementation of the search algorithm described in the article.

    Attributes
    ----------
    ac : AccessStructure

    k : int
        The size of the secret.
    base_ring : GF
        The base ring of all vector and matrix multiplications.
    eps : list
        A list of tuples of code vector indices.
    parameters : tuple
        The parameters of all participants.
    height : int
        The height of the search tree.
    """
    def __init__(self,
                 ac: AccessStructure,
                 k: int,
                 base_ring: GF,
                 eps: Epsilon,
                 parameters: Tuple[int, ...],
                 height: int) -> None:
        self.ac = ac
        self.k = k
        self.base_ring = base_ring
        self.eps = eps
        self.parameters = parameters
        self.height = height

    def sequential_search(self,
                          level: int,
                          s_m: Dict[str, Vector],
                          s_n: Set[int],
                          aa: List[matrix],
                          ba: List[matrix],
                          ca: List[Vector],
                          skip: float) -> Union[List[Vector], List]:
        """
        Sequential implementation of the search algorithm.

        Parameters
        ----------
        level : int
            The current level of the search tree.
        s_m : dict
            A dictionary of the edge labels on the path to the current node.
        s_n : set
            The set of levels on the path to the current node for which the edge label is a
            singleton set.
        aa : list
            A list of matrices :math:`A_i(\texttt{n})`.
        ba : list
            A list of matrices :math:`B_i(\texttt{n}')`.
        ca : list
            The list of candidate vectors.
        skip : float
            The skip parameter passed as argument.

        Returns
        -------
        res : list
            An empty list if there is no suitable sets of vectors, the list of suitable
            sets of vectors otherwise.
        """
        if level > self.height:
            return ca

        res = []

        eps_for_this_level = "".join(str(i) for i in self.eps[level - 1])
        x_i = self.ac.gamma_min[int(eps_for_this_level[0])]
        labels = self._break_labels(list(s_m.values()))
        span_of_labels = span(list(i.c for i in labels), self.base_ring)

        lab = []
        for potential_label in span_of_labels:
            label = Vector(potential_label, self.base_ring, self.parameters)
            if p_support(label) <= x_i:
                lab.append(label)

        lab = self._break_labels(lab)
        b, ab, bb, cb = self._determine_d_plus(level, x_i, lab, s_n, aa, ba, ca)

        if b:
            res = self.sequential_search(level + 1, s_m, s_n, ab, bb, cb, skip)
            if res:
                return res

        generated_labels = list(generate_label(self.ac.participants, self.parameters, x_i, self.base_ring, span_of_labels))
        generated_labels = random.sample(generated_labels, k=int((1 - skip) * len(generated_labels)))

        for potential_label in generated_labels:
            s_n = s_n | {level}
            s_m = {**s_m, eps_for_this_level: potential_label}
            b, ab, bb, cb = self._determine_d_plus(level, x_i, potential_label, s_n, aa, ba, ca)

            if b:
                res = self.sequential_search(level + 1, s_m, s_n, ab, bb, cb, skip)
                if res:
                    return res
        return res

    def parallel_search(self,
                        level: int,
                        s_m: Dict[str, Vector],
                        s_n: Set[int],
                        aa: List[matrix],
                        ba: List[matrix],
                        ca: List[Vector],
                        skip: float,
                        task_queue: Queue,
                        is_finished: Event) -> None:
        """
        The parallel implementation of the search algorithm.

        When the algorithm reaches level :math:`r` of the search tree the method
        puts the parameters to the ``task_queue``. The other processes can use these
        parameters to run method ``sequential_search()`` to find a solution (if there
        are any).

        Parameters
        ----------
        level : int
            The current level of the search tree.
        s_m : dict
            A dictionary of the edge labels on the path to the current node.
        s_n : set
            The set of levels on the path to the current node for which the edge label is a
            singleton set.
        aa : list
            A list of matrices :math:`A_i(\texttt{n})`.
        ba : list
            A list of matrices :math:`B_i(\texttt{n}')`.
        ca : list
            The list of candidate vectors.
        skip : float
            The skip parameter passed as argument.
        task_queue : Queue
            The task queue for other processes.
        is_finished : Event
            A shared event between the processes. If set, a solution is found (positive or
            negative) and the worker processes terminate.

        """
        if level == self.height // 2 + 1:
            task_queue.put((level, s_m, s_n, aa, ba, ca, skip))
            return

        eps_for_this_level = "".join(str(i) for i in self.eps[level - 1])
        x_i = self.ac.gamma_min[int(eps_for_this_level[0])]
        labels = self._break_labels(list(s_m.values()))
        span_of_labels = span(list(i.c for i in labels), self.base_ring)

        lab = []
        for potential_label in span_of_labels:
            label = Vector(potential_label, self.base_ring, self.parameters)
            if p_support(label) <= x_i:
                lab.append(label)

        lab = self._break_labels(lab)
        b, ab, bb, cb = self._determine_d_plus(level, x_i, lab, s_n, aa, ba, ca)

        if b and not is_finished.is_set():
            self.parallel_search(level + 1, s_m, s_n, ab, bb, cb, skip, task_queue, is_finished)
        elif is_finished.is_set():
            return

        generated_labels = list(generate_label(self.ac.participants, self.parameters, x_i, self.base_ring, span_of_labels))
        generated_labels = random.sample(generated_labels, k=int((1 - skip) * len(generated_labels)))

        for potential_label in generated_labels:
            s_n = s_n | {level}
            s_m = {**s_m, eps_for_this_level: potential_label}
            b, ab, bb, cb = self._determine_d_plus(level, x_i, potential_label, s_n, aa, ba, ca)

            if b and not is_finished.is_set():
                self.parallel_search(level + 1, s_m, s_n, ab, bb, cb, skip, task_queue, is_finished)
            elif is_finished.is_set():
                return

    def is_valid_gen_vec_constr(self, possible_matrix: matrix) -> Tuple[bool, str]:
        """Checks conditions V1 and V2 of Theorem 2.1."""
        def create_submatrix():
            """Return matrix G[X]."""
            f = 0
            cols = []
            for i, s in enumerate(self.parameters, start=1):
                if i in x:
                    cols += list(range(f, f+s))
                f += s
            return possible_matrix.matrix_from_columns(cols)

        def linear_combinations_of_unit_vectors():
            """Return the non-zero linear combinations of the unit vectors."""
            res = []
            mat = matrix(unit_vectors).T
            for com in product(self.base_ring.list(), repeat=len(unit_vectors)):
                res.append(mat.linear_combination_of_columns(com))
            return res[1:]

        unit_vectors = [jth_unit_vector(j+1, possible_matrix.nrows(), self.base_ring) for j in range(self.k)]

        # check condition V1
        for x in self.ac.gamma:
            submat = create_submatrix()
            for unit in unit_vectors:
                for possible_combination in product(self.base_ring.list(), repeat=submat.ncols()):
                    if submat.linear_combination_of_columns(possible_combination) == unit:
                        break
                else:
                    return False, f"V1, unit vector {unit} cannot be expressed as a linear combination " \
                                  f"of the columns of matrix G[{set(x)}]"

        # check condition V2
        lin_comb_of_units = linear_combinations_of_unit_vectors()
        for x in self.ac.delta:
            submat = create_submatrix()
            for possible_combination in product(self.base_ring.list(), repeat=submat.ncols()):
                if submat.linear_combination_of_columns(possible_combination) in lin_comb_of_units:
                    return False, f"V2, the linear combination {possible_combination} of columns of matrix " \
                                  f"G[{set(x)}] results in a linear combination of unit vectors"
        return True, ""

    def _count_increment_leaves_below(self,
                                      level: int,
                                      x_i: Set[int],
                                      leaf_counter: Value) -> None:
        n_leaves = (self.base_ring.order() ** sum(self.parameters[i - 1] for i in x_i)) ** (self.height - level)
        with leaf_counter.get_lock():
            leaf_counter += n_leaves

    def _d_plus(self,
                label: Union[Vector, List[Vector]],
                s_a: Set[int],
                e_js: vector,
                b_comp: Set[int],
                node_compl_parameters: Tuple[int, ...],
                aa: List[matrix],
                ba: List[matrix],
                ca: List[Vector]) -> Tuple[bool, List[matrix], List[matrix], List[Vector]]:
        """
        Determines the value of :math:`D^+(\\texttt{n})` and :math:`D^-(\\texttt{n})` for nodes.

        The two boolean statements are the following:

        - The value of :math:`D^+(\\texttt{n})` is true iff :math:`\\texttt{n}` is a candidate
          node and the :math:`d^+(\\Delta)`-property for :math:`\\mathcal{E}(\\texttt{n})`
          holds for any set of vectors corresponding to node :math:`\\texttt{n}`
        - The value of :math:`D^-(\\texttt{n})` is true iff none of the sets corresponding to
          candidate leafs on the left side of :math:`\\texttt{n}` has the :math:`d^-(\\Delta)`-property.

        Parameters
        ----------
        label : Vector or list of Vectors
            The edge label to the current node
        s_a
        e_js
        b_comp
        node_compl_parameters
        aa
        ba
        ca

        Returns
        -------

        """
        d = self.ac.delta_max
        base_ring = self.base_ring
        parameters = self.parameters
        ab = deepcopy(aa)
        bb = deepcopy(ba)

        if isinstance(label, Vector) and not label.is_zero():
            # Lemma 5.10
            stop = False

            for i in range(len(d)):
                c_proj_to_d_compl = projection(label, self.ac.participants - d[i + 1], parameters)
                f = e_js - c_proj_to_d_compl.c * aa[i]
                c_proj_ba = c_proj_to_d_compl.c * ba[i]

                b_idx = next((j for j, x in enumerate(c_proj_ba) if x), None)
                if b_idx is not None:
                    c_proj_b_inv = inverse_mod(int(c_proj_ba[b_idx]), base_ring.order())
                    temp = vector(ba[i][:, b_idx].list(), base_ring)
                    bb[i] = ba[i] - temp.outer_product(c_proj_b_inv * c_proj_to_d_compl.c * ba[i])
                    if not f.is_zero():
                        ab[i] = aa[i] + temp.outer_product(c_proj_b_inv * f)
                else:
                    stop = not f.is_zero()
                    if stop:
                        break
            return not stop, ab, bb, ca + [label]
        elif isinstance(label, list) and ca and sum(s_a) == max(s_a) * (max(s_a) + 1) // 2:
            # Lemma 5.11
            e_js_zero = vector(e_js.list() + [0] * sum(node_compl_parameters), base_ring)

            e_jm = [jth_unit_vector(self.eps[m - 1][1], self.k, base_ring) if m in s_a else None for m in range(1, max(s_a) + 1)]
            c_m_proj = [projection(ca[m - 1], b_comp, parameters) if m in s_a else None for m in range(1, max(s_a) + 1)]
            e_jm_c_m_proj = [vector(e.list() + c.list(), base_ring) if e is not None else None for e, c in zip(e_jm, c_m_proj)]

            potential_bs = list(product(base_ring.list(), repeat=len(s_a)))

            for potential_b in random.sample(potential_bs, k=len(potential_bs)):
                if sum(potential_b[m - 1] * e_jm_c_m_proj[m - 1] for m in s_a) == e_js_zero:
                    res = sum(potential_b[m - 1] * ca[m - 1].c for m in s_a)
                    return True, ab, bb, ca + [Vector(res, base_ring, parameters)]
        return False, aa, ba, ca

    def _determine_d_plus(self,
                          level: int,
                          x_i: Set[int],
                          potential_label: Union[Vector, List[Vector]],
                          s_n: Set[int],
                          aa: List[matrix],
                          ba: List[matrix],
                          ca: List[Vector]) -> Tuple[bool, List[matrix], List[matrix], List[Vector]]:
        compl_of_this_node = self.ac.participants - x_i
        share_size_of_compl = tuple(self.parameters[i - 1] for i in compl_of_this_node)

        return self._d_plus(potential_label,
                            s_n,
                            jth_unit_vector(self.eps[level - 1][1], self.k, self.base_ring),
                            compl_of_this_node,
                            share_size_of_compl,
                            aa, ba, ca)

    def _break_labels(self, labels: Union[Vector, List[Vector]]) -> List[Vector]:
        if not labels:
            return [Vector.all_zero(self.base_ring, self.parameters)]
        res = []
        for label in labels:
            if isinstance(label, Vector):
                res.append(label)
            else:
                res += self._break_labels(label)
        return res
