from pathlib import Path

from src.cdm import parse_cdm

import numpy as np
import random

POPULATION_SIZE = 50
MAX_GENERATIONS = 1000
MUTATION_RATE = 0.1
DESIRED_MISS_DISTANCE = 5000


def fitness(chromosome, state_vector, miss_distance, fuel_cost_weight=1):
    return abs(sum(chromosome))
    # # Simulate new trajectory (placeholder for actual propagation logic)
    # new_miss_distance = simulate_miss_distance(state_vector, chromosome)
    # fuel_cost = calculate_fuel_cost(chromosome)
    #
    # # Fitness is a combination of safety (miss distance) and fuel efficiency
    # return (new_miss_distance / DESIRED_MISS_DISTANCE) - fuel_cost_weight * fuel_cost


def initialize_population(population_size):
    return [np.random.uniform(0.0, 1.0, size=3) for _ in range(population_size)]


def simulate_miss_distance(state_vector, maneuver):
    # Apply maneuver to state vector and recalculate miss distance
    perturbed_vector = state_vector + maneuver
    return np.linalg.norm(perturbed_vector)


def calculate_fuel_cost(maneuver):
    return np.linalg.norm(maneuver)


def select(population, fitnesses):
    total_fitness = sum(fitnesses)
    probabilities = [f / total_fitness for f in fitnesses]
    return population[np.random.choice(len(population), p=probabilities)]


def crossover(parent1, parent2):
    alpha = np.random.uniform(0, 1)
    return alpha * parent1 + (1 - alpha) * parent2


def mutate(chromosome, mutation_rate):
    if random.random() < mutation_rate:
        return chromosome + np.random.uniform(-0.5, 0.5, size=3)
    return chromosome


def genetic_algorithm(cdm1, cdm2):
    population = initialize_population(POPULATION_SIZE)
    state_vector = np.array([41841.22, -5327.61, -18.52])

    for generation, i in enumerate(range(MAX_GENERATIONS)):
        # Calculate fitness for each chromosome
        fitnesses = [fitness(child, state_vector, DESIRED_MISS_DISTANCE) for child in population]
        print(f"Gen-{i}: {fitnesses[0]}")

        # Create new population
        new_population = []
        for _ in range(POPULATION_SIZE // 2):
            # Select parents
            parent1 = select(population, fitnesses)
            parent2 = select(population, fitnesses)

            # Crossover
            child1 = crossover(parent1, parent2)
            child2 = crossover(parent2, parent1)

            # Mutate
            child1 = mutate(child1, MUTATION_RATE)
            child2 = mutate(child2, MUTATION_RATE)

            new_population.extend([child1, child2])

        # Replace old population
        population = new_population

    # Return best solution
    fitnesses = [fitness(c, state_vector, DESIRED_MISS_DISTANCE) for c in population]
    print(f"Best fitness: {fitnesses[0]}")
    best_chromosome = population[np.argmax(fitnesses)]
    return best_chromosome


def main() -> None:
    cdm1 = parse_cdm(Path("data/CSPOC_9.xml"))
    print(cdm1)
    cdm2 = parse_cdm(Path("data/CAESAR_TRJ_12.xml"))
    print(cdm2)

    print(genetic_algorithm(cdm1, cdm2))


if __name__ == "__main__":
    main()
