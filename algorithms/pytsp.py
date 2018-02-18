from algorithms.genetic_algorithm import GeneticAlgorithm
from algorithms.linear_programming import LinearProgramming
from algorithms.local_optimization import LocalOptmizationHeuristics
from algorithms.tour_construction import TourConstructionHeuristics


class pyTSP(
    GeneticAlgorithm,
    LinearProgramming,
    LocalOptmizationHeuristics,
    TourConstructionHeuristics):

    algorithms = (
        'nearest_neighbor',
        'nearest_insertion',
        'farthest_insertion',
        'cheapest_insertion',
        'pairwise_exchange',
        'node_insertion',
        'edge_insertion',
        'ILP_solver'
        )
