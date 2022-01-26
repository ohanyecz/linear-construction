import argparse
from multiprocessing import Process, Value, Manager, current_process
from os import cpu_count
import random
from time import perf_counter, sleep
from threading import Event, Thread
from typing import List
from queue import Queue  # import only for typing

from sage.all import factor, GF, matrix, span
from tqdm import tqdm

from linearconstruction.utils import FileType
from linearconstruction import *


try:
    from math import comb
except ImportError:
    from math import factorial

    def comb(n, k):
        return factorial(n) / (factorial(k) * factorial(n - k))


def estimate_leaf_number() -> int:
    p_sum = sum(parameters)
    x_sum = [sum(parameters[j - 1] for j in x) for x in ac.gamma_min.values()]

    if p_sum >= r * k:
        return q ** (k * sum(x_sum))
    return comb(r * k, p_sum) * q ** (p_sum * max(x_sum))


def show_progressbar(leaf_counter: Value,
                     is_finished: Event) -> None:
    """
    Show progressbar if verbosity is set.

    The progressbar shows the number of checked leaves in the search tree
    which is stored in a shared value.

    Parameters
    ----------
    leaf_counter : multiprocessing.Value
        The number of leaves checked in the search tree.
    is_finished : threading.Event
        ``True`` if there is or is not a set of candidate vectors, ``False`` otherwise.
    """
    pbar = tqdm(total=estimate_leaf_number(),
                bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}]",
                desc="Leaves",
                dynamic_ncols=True)
    old_value = leaf_counter.value
    while not is_finished.is_set():
        v = leaf_counter.value
        if v > old_value:
            pbar.update(v - old_value)
            old_value = v
    pbar.close()


def process_tasks(task_queue: Queue,
                  done_queue: Queue,
                  is_finished: Event) -> None:
    """
    Processes a task from the *task_queue* and puts the result to *done_queue*.

    A result is a tuple of two objects:

    - the first object is a *list* containing the solution. The solution can be an
    empty list which indicates that at a specific edge of the search tree the
    function ``d_plus()`` returns ``False``. If the list is not empty, then the list
    contains a list of candidate vectors suitable to define a secret sharing scheme.
    - the second object is an *int* indicating the number of leaves skipped when the
    function ``d_plus()`` returns ``False``, 1 otherwise.
    """
    while not is_finished.is_set():
        params = task_queue.get()
        if params != "DONE":
            res = search.sequential_search(*params)
            done_queue.put(res)
        else:
            break
    done_queue.put("STOP")


def submit_tasks(task_queue: Queue,
                 is_finished: Event) -> None:
    """
    Submits a task to a process from the task queue.

    A ``"STOP"`` signal will be put to *task_queue* at the end of the running. This
    indicates that no more task will be sent later and the threads and processes
    can terminate.

    Parameters
    ----------
    task_queue : Queue
        The queue of the tasks that should be processed.
    is_finished : threading.Event
        ``True`` if a suitable set of vectors are found or there is no suitable
        set of vectors. ``False`` otherwise
    """
    s_m = {}
    s_n = set()
    d_comp = [list(ac.participants - ac.delta_max[i]) for i in ac.delta_max.keys()]
    id_matrix_sizes = [sum(parameters[i - 1] for i in d_comp[j]) for j in range(len(d_comp))]
    aa = [matrix(finite_field, [[0] * k] * i) for i in id_matrix_sizes]
    ba = [matrix.identity(i) for i in id_matrix_sizes]
    ca = []

    search.parallel_search(1, s_m, s_n, aa, ba, ca, args.skip, task_queue, is_finished)
    task_queue.put("DONE")


def monitor_finished_tasks(done_queue: Queue,
                           is_finished: Event,
                           result: List) -> None:
    """
    Checks the content of *done_queue*.

    Repeatedly checks the content of *done_queue* for a solution, sets an event
    shared between the processes and copies the solution to a shared variable.

    The event is set if either there is a solution in the *done_queue* or a
    ``'STOP'`` signal is found.

    Parameters
    ----------
    done_queue : Queue
        The queue of the finished processes.
    is_finished : threading.Event
        ``True`` if a suitable set of vectors are found or there is no suitable
        set of vectors. ``False`` otherwise
    leaf_counter : multiprocessing.Value
        Counts the number of checked leaves of the search tree. Used for
        showing the progressbar if verbosity is set.

    See Also
    --------
    submit_tasks : For how the elements in *done_queue* are built.
    """
    while not is_finished.is_set():
        solution = done_queue.get()
        if solution == "STOP":
            is_finished.set()
        elif solution:
            result.extend(solution)
            is_finished.set()


def integer_representation(mat: matrix) -> matrix:
    """Return a new matrix with integer representation of elements of *mat*."""
    return matrix(list(map(lambda x: finite_field_map[x], row)) for row in mat)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="A linear construction of secret sharing schemes. See the manual for "
                                                 "usage examples.")

    parser.add_argument("participants",
                        type=int,
                        help="The number of participants in the scheme")
    parser.add_argument("parameters",
                        help="The amount of share to give each participant. Each parameter should be separated by "
                             "comma.")
    parser.add_argument("order",
                        type=int,
                        help="The order of the finite field. Should be prime power")
    parser.add_argument("k",
                        type=int,
                        help="The cardinality of the set of possible secrets")
    parser.add_argument("minimal",
                        nargs="+",
                        help="The minimal sets of the qualified groups.")
    parser.add_argument("-s", "--seed",
                        type=int,
                        default=None,
                        help="Seed the random number generator (default: %(default)s)")
    parser.add_argument("-S", "--skip",
                        type=float,
                        default=.0,
                        help="Skip the specified portion of the edges in the search tree")
    parser.add_argument("-o", "--output",
                        type=FileType("w+"),
                        default="-",
                        help="Save the solution with the arguments passed (default: stdout)")
    parser.add_argument("-f", "--force",
                        action="store_true",
                        help="If `True` override the output file if exists. Otherwise, save to an output file with "
                             "prefix passed to argument --output. (default: %(default)s)")
    parser.add_argument("-v", "--verbose",
                        action="store_true",
                        help="Be verbose.")
    parser.add_argument("--version",
                        action="version")

    access_structure_group = parser.add_argument_group(title="Access structure modifiers")
    access_structure_group.add_argument("-d", "--dual",
                                        action="store_true",
                                        help="Apply the algorithm to the dual of the specified access "
                                             "structure (default: %(default)s)")

    parallel_group = parser.add_argument_group(title="Parameters of parallelization")
    parallel_group.add_argument("-P", "--processors",
                                type=int,
                                default=cpu_count(),
                                help="Run the algorithm on the specified number of processors (default: cpu count)")
    parallel_group.add_argument("-Q", "--queuesize",
                                type=int,
                                default=100,
                                help="Set the size of the queue (default: %(default)s)")

    args = parser.parse_args()

    random.seed(args.seed)
    ac = AccessStructure.from_iterable(args.participants, args.minimal, create_dual=args.dual)
    r = len(ac.gamma_min.keys())
    k = args.k
    if len(list(factor(args.order))) > 1:
        raise ValueError(f"Order of the finite field is not a prime power.")
    q = args.order
    if q > 2:
        finite_field = GF(q, impl="givaro")
        finite_field_map = {i: i.integer_representation() for i in finite_field.list()}
    else:
        finite_field = GF(q)
    eps = epsilon(r, k)
    p = args.parameters
    parameters = tuple(int(i) for i in p.split(",")) if "," in p else int(p)

    task_queue = Manager().Queue(maxsize=args.queuesize)
    done_queue = Manager().Queue(maxsize=100)
    is_finished = Manager().Event()
    leaf_counter = Value("i", 0)
    result = Manager().list()

    search = SearchAlgorithm(ac, k, finite_field, eps, parameters, r * k)

    if args.verbose:
        print(f"Created a '{finite_field}'")
        print(f"Created '{ac}'")
        print(f"The height of the search tree: {r * k}")
        print(f"Parent process: PID={current_process().pid}")

    if args.verbose:
        progressbar_thread = Thread(target=show_progressbar,
                                    args=(leaf_counter, is_finished)).start()

    sleep(0.1)
    monitor_process = Thread(target=monitor_finished_tasks,
                             args=(done_queue, is_finished, result))
    monitor_process.start()

    task_builder_process = Process(target=submit_tasks,
                                   args=(task_queue, is_finished))
    worker_processes = [Process(target=process_tasks,
                                args=(task_queue, done_queue, is_finished)) for _ in range(args.processors)]
    for p in worker_processes:
        p.start()

    start = perf_counter()
    task_builder_process.start()
    is_finished.wait()
    delta = perf_counter() - start

    task_builder_process.terminate()
    task_builder_process.join()
    for p in worker_processes:
        p.terminate()
    for p in worker_processes:
        p.join()
    monitor_process.join()

    if result:
        unit_vectors = [jth_unit_vector(j[1], k, finite_field) for j in eps]
        generator_matrix = matrix(finite_field, [e.list() + v.c.list() for e, v in zip(unit_vectors, result)])
        parity_check_matrix = generator_matrix.right_kernel_matrix()
        gen_vec_matrix = parity_check_matrix[:, 2:]
        if search.is_valid_gen_vec_constr(gen_vec_matrix):
            args.output.write(f"Participants: {ac.participants}\n")
            args.output.write(f"Parameters: {parameters}\n")
            args.output.write(f"Minimal qualified groups: {str(ac.gamma_min)}\n")
            args.output.write(f"Maximal forbidden groups: {str(ac.delta_max)}\n")
            args.output.write(f"Dual: {args.dual}\n")
            args.output.write(f"Finite field: {str(finite_field)}\n")
            args.output.write(f"Size of the secret: {k}\n")
            args.output.write(f"Skip: {args.skip}\n")
            args.output.write(f"Seed: {args.seed}\n")
            args.output.write(f"Number of processors: {args.processors}\n")
            args.output.write(f"Running time: {delta} seconds\n\n")
            if q > 2:
                generator_matrix = integer_representation(generator_matrix)
                parity_check_matrix = integer_representation(parity_check_matrix)
                gen_vec_matrix = integer_representation(gen_vec_matrix)
            args.output.write(f"The generator matrix:\n")
            for row in generator_matrix:
                args.output.write(str(row) + "\n")
            args.output.write(f"\nThe parity check matrix:\n")
            for row in parity_check_matrix:
                args.output.write(str(row) + "\n")
            args.output.write(f"\nThe Generalized Vector Space Construction:\n")
            for row in gen_vec_matrix:
                args.output.write(str(row) + "\n")
        else:
            args.output.write(f"The candidate vectors are not valid.")
    else:
        args.output.write(f"There does not exists a general vector space construction with the specified parameters!")
    print("done.")
    args.output.close()
