import argparse
from multiprocessing import Process, Value, Manager
from os import cpu_count
import random
from threading import Event, Thread
from queue import Queue  # import only for typing

from sage.all import factor, GF
from tqdm import tqdm

from linearconstruction.utils import FileType
import linearconstruction


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
    ...


# TODO: a konkrét működésre kéne formázni
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
    j = 0
    while not is_finished.is_set():
        if j == 1337:
            task_queue.put((linearconstruction.epsilon(3, 2), 10))
        else:
            task_queue.put((tuple(), 1))
        j += 1
    task_queue.put(("STOP", 0))


# TODO: ha van megoldás, csináljunk is vele valamit
def monitor_finished_tasks(done_queue: Queue,
                           is_finished: Event,
                           leaf_counter: Value) -> None:
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
        solution, n_leaves = done_queue.get()
        if solution == "STOP":
            is_finished.set()
        elif solution:
            is_finished.set()
        else:
            with leaf_counter.get_lock():
                leaf_counter.value += n_leaves


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
    ac = linearconstruction.AccessStructure.from_iterable(args.participants, args.minimal, create_dual=args.dual)
    r = len(ac.gamma_min.keys())
    k = args.k
    if len(list(factor(args.order))) > 1:
        raise ValueError(f"Order of the finite field is not a prime power.")
    q = args.order
    finite_field = GF(q)
    eps = linearconstruction.epsilon(r, k)
    p = args.parameters
    parameters = tuple(int(i) for i in p.split(",")) if "," in p else int(p)

    task_queue = Manager().Queue(maxsize=args.queuesize)
    done_queue = Manager().Queue(maxsize=100)
    is_finished = Event()
    leaf_counter = Value("i", 0)

    if args.verbose:
        print(f"Created a '{finite_field}'")
        print(f"Created '{ac}'")
        print(f"The height of the search tree: {r * k}")

    if args.verbose:
        progressbar_thread = Thread(target=show_progressbar,
                                    args=(leaf_counter, is_finished)).start()

    monitor_thread = Thread(target=monitor_finished_tasks,
                            args=(done_queue, is_finished, leaf_counter)).start()
    task_builder_thread = Thread(target=submit_tasks,
                                 args=(done_queue, is_finished)).start()

    # worker_processes = [Process(target=process_tasks,
    #                             args=(task_queue, done_queue, is_finished)) for _ in range(args.processes)]
    # for p in worker_processes:
    #     p.start()

    is_finished.wait()

    args.output.close()

#TODO: kiírni a futás végén, hogy a program hova mentette a fájlt
#TODO: a traverse argumentumot értelmesen megcsinálni
