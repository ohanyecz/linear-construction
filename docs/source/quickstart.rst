.. _quickstart:

==========
Quickstart
==========

If you have a working version of Sage installed on your system, it is easy to run the algorithm using the command
``sage -python linear-construction.py``. However, it requires some command line arguments.

For example, let's run the algorithm on for participants and let the minimal qualified sets be
:math:`[\Gamma]^- = \{ \{a, b\}, \{c, d\}, \{b, c\} \}`. Let :math:`k = 2` be the size of the secret and
:math:`\text{GF}(2)` be the field we work with. Each participant must have a parameter telling the size of the share
they receive. Let :math:`p_1 = p_4 = 2` and :math:`p_2 = p_3 = 3`. Then the command we should run is::

    sage -python linear-construction.py 4 2,3,3,2 2 2 ab cd bc

The arguments passed here are required arguments and the order should be given is the following:

- the number of participants,
- the parameter of each participants separated by comma (``,``),
- the order of the finite field (this should be a prime power),
- the size of the secret, and
- the minimal qualified groups separated by spaces.

By default, the results (positive or negative as well) are written to ``stdout``. The implementation uses a random
number generator to shuffle the search tree so the result can be different for you::

    Participants: {1, 2, 3, 4}
    Parameters: (2, 3, 3, 2)
    Minimal qualified groups: {1: {1, 2}, 2: {3, 4}, 3: {2, 3}}
    Maximal forbidden groups: {1: {2, 4}, 2: {1, 4}, 3: {1, 3}}
    Dual: False
    Finite field: Finite Field of size 2
    Size of the secret: 2
    Skip: 0.0
    Seed: None
    Number of processors: 2
    Running time: 1.1475847399997292 seconds

    The generator matrix:
    (1, 0, 1, 0, 0, 1, 1, 0, 0, 0, 0, 0)
    (1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1)
    (1, 0, 0, 0, 1, 1, 0, 1, 1, 0, 0, 0)
    (0, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0)
    (0, 1, 0, 0, 0, 0, 0, 1, 0, 1, 1, 0)
    (0, 1, 0, 0, 0, 1, 0, 1, 0, 1, 0, 0)

    The parity check matrix:
    (1, 0, 0, 0, 1, 0, 1, 0, 0, 0, 0, 1)
    (0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 0, 1)
    (0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0)
    (0, 0, 0, 1, 1, 0, 0, 0, 1, 0, 0, 1)
    (0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 1, 1)
    (0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0, 1)

    The Generalized Vector Space Construction:
    (0, 0, 1, 0, 1, 0, 0, 0, 0, 1)
    (0, 0, 1, 0, 0, 0, 1, 1, 0, 1)
    (1, 0, 0, 0, 1, 0, 0, 0, 0, 0)
    (0, 1, 1, 0, 0, 0, 1, 0, 0, 1)
    (0, 0, 0, 1, 1, 0, 1, 1, 1, 1)
    (0, 0, 0, 0, 0, 1, 1, 1, 0, 1)

The first 11 rows are there for a reminder if the file is inspected at a later time.

The output destination can be changed by using the option ``--output`` followed by the name of the file.

The implementation is using process-based parallelism. By default, it uses all available processors it finds which
can slow down the computer significantly. The option ``--processors`` followed by a number tells the program to run
the algorithm on the specified number of processors.

Another important option is ``--skip``. This should be a float in :math:`[0..1)` which specifies the proportion of
the outgoing edges to be *skipped*. For example, ``--skip 0.7`` tells the implementation that only 30% of the
edges should be visited, the other 70% should be ignored.

The ``--dual`` option tells the algorithm to calculate the dual access structure of the *passed* access structure
and run the algorithm on the dual. In the output the row `Dual: True` means that the minimal qualified groups and
the maximal forbidden groups are the dual access structure, **not** the access structure passed as arguments.

The complete list of arguments can be listed using the command ``sage -python linear-construction.py --help``::

    usage: linear-construction.py [-h] [-s SEED] [-S SKIP] [-o OUTPUT] [-f] [-v] [--version] [-d] [-P PROCESSORS] [-Q QUEUESIZE] participants parameters order k minimal [minimal ...]

    A linear construction of secret sharing schemes. See the manual for usage examples.

    positional arguments:
      participants          The number of participants in the scheme
      parameters            The amount of share to give each participant. Each parameter should be separated by comma.
      order                 The order of the finite field. Should be prime power
      k                     The cardinality of the set of possible secrets
      minimal               The minimal sets of the qualified groups.

    optional arguments:
      -h, --help            show this help message and exit
      -s SEED, --seed SEED  Seed the random number generator (default: None)
      -S SKIP, --skip SKIP  Skip the specified portion of the edges in the search tree
      -o OUTPUT, --output OUTPUT
                            Save the solution with the arguments passed (default: stdout)
      -f, --force           If `True` override the output file if exists. Otherwise, save to an output file with prefix passed to argument --output. (default: False)
      -v, --verbose         Be verbose.
      --version             show program's version number and exit

    Access structure modifiers:
      -d, --dual            Apply the algorithm to the dual of the specified access structure (default: False)

    Parameters of parallelization:
      -P PROCESSORS, --processors PROCESSORS
                            Run the algorithm on the specified number of processors (default: cpu count)
      -Q QUEUESIZE, --queuesize QUEUESIZE
                            Set the size of the queue (default: 100)
