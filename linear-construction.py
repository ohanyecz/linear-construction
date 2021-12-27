import argparse
from os import cpu_count

from utils import FileType


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
                        help="The order of the finite field. Should be prime power")
    parser.add_argument("k",
                        type=int,
                        help="The cardinality of the set of possible secrets")
    parser.add_argument("minimal",
                        nargs="+",
                        help="The minimal sets of the qualified groups.")

    parser.add_argument("-t", "--traverse",
                        help="Run the algorithm on all possible combination of parameters passed. The optional "
                             "argument 'parameters' ignored.")
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
    access_structure_group.add_argument("-M", "--maximal",
                                        nargs="+",
                                        help="The maximal sets of the unqualified groups")
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


#TODO: kiírni a futás végén, hogy a program hova mentette a fájlt
#TODO: a traverse argumentumot értelmesen megcsinálni
