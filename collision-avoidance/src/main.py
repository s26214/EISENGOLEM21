from dataclasses import dataclass
from math import sqrt
from pathlib import Path
from typing import List
import random

from src.cdm import parse_cdm, Segment, RelativeMetadataData, CDM, RelativeStateVector

# Genetic Algorithm Parameters
POPULATION_SIZE = 50
MAX_GENERATIONS = 100
MUTATION_RATE = 0.1
DESIRED_MISS_DISTANCE = 5000


@dataclass
class Chromosome:
    """Represents a solution for the genetic algorithm."""
    thrust_r: float  # Radial thrust component
    thrust_t: float  # Tangential thrust component
    thrust_n: float  # Normal thrust component
    duration: float  # Duration of thrust (seconds)


def simulate_event(cdm: CDM, chromosome: Chromosome) -> None:
    """Simulates the event by applying the thrust specified in the chromosome and updates the relative_metadata_data."""
    if not cdm.segments:
        raise ValueError("No segments found in CDM.")

    # Assume we are using the first segment for simulation
    segment = cdm.segments[0]

    if not segment.data.state_vector:
        raise ValueError("State vector is required in the segment data.")

    # Apply the maneuver to the velocity components
    sv = segment.data.state_vector
    sv.x_dot += chromosome.thrust_r * chromosome.duration
    sv.y_dot += chromosome.thrust_t * chromosome.duration
    sv.z_dot += chromosome.thrust_n * chromosome.duration

    # Update the position based on the updated velocities
    sv.x += sv.x_dot * chromosome.duration
    sv.y += sv.y_dot * chromosome.duration
    sv.z += sv.z_dot * chromosome.duration

    # Update the state_vector in the segment
    segment.data.state_vector = sv

    # Now update the relative_metadata_data based on the new state_vector
    relative_state_vector = RelativeStateVector(
        relative_position_r=sv.x,
        relative_position_t=sv.y,
        relative_position_n=sv.z,
        relative_velocity_r=sv.x_dot,
        relative_velocity_t=sv.y_dot,
        relative_velocity_n=sv.z_dot
    )

    cdm.relative_metadata_data.relative_state_vector = relative_state_vector


def calculate_fitness(relative_metadata: RelativeMetadataData, fuel_consumption: float) -> float:
    """Calculates fitness based on miss distance and fuel consumption."""
    miss_distance = relative_metadata.miss_distance
    relative_speed = relative_metadata.relative_speed

    distance_divisor = sqrt(miss_distance + 0.1)

    fitness = max(0.0, 1000 / distance_divisor - 1e+3 * fuel_consumption)
    fitness += max(0.0, 10 - relative_speed / 10)  # Bonus for low relative speed
    return fitness


def initialize_population(population_size: int) -> List[Chromosome]:
    """Generates an initial population of random chromosomes."""
    return [
        Chromosome(
            thrust_r=random.uniform(-1e-2, 1e-2),
            thrust_t=random.uniform(-1e-2, 1e-2),
            thrust_n=random.uniform(-1e-2, 1e-2),
            duration=random.uniform(1, 10)
        )
        for _ in range(population_size)
    ]


def crossover(parent1: Chromosome, parent2: Chromosome) -> Chromosome:
    """Performs crossover between two chromosomes."""
    alpha = random.uniform(0, 1)
    return Chromosome(
        thrust_r=alpha * parent1.thrust_r + (1 - alpha) * parent2.thrust_r,
        thrust_t=alpha * parent1.thrust_t + (1 - alpha) * parent2.thrust_t,
        thrust_n=alpha * parent1.thrust_n + (1 - alpha) * parent2.thrust_n,
        duration=alpha * parent1.duration + (1 - alpha) * parent2.duration
    )


def mutate(chromosome: Chromosome, mutation_rate: float) -> Chromosome:
    """Mutates a chromosome with a certain probability."""
    if random.random() < mutation_rate:
        return Chromosome(
            thrust_r=chromosome.thrust_r + random.uniform(-1e-4, 1e-4),
            thrust_t=chromosome.thrust_t + random.uniform(-1e-4, 1e-4),
            thrust_n=chromosome.thrust_n + random.uniform(-1e-4, 1e-4),
            duration=max(0.0, chromosome.duration + random.uniform(-0.3, 0.3))
        )
    return chromosome


def genetic_algorithm(cdm: CDM):
    """Runs the genetic algorithm to optimize the maneuver."""
    population = initialize_population(POPULATION_SIZE)

    for generation in range(MAX_GENERATIONS):
        fitnesses = []
        fuel_consumptions = []
        for chromosome in population:
            simulate_event(cdm, chromosome)
            fuel_consumption = (
                abs(chromosome.thrust_r) +
                abs(chromosome.thrust_t) +
                abs(chromosome.thrust_n)
            ) * chromosome.duration
            fitness = calculate_fitness(cdm.relative_metadata_data, fuel_consumption)
            fitnesses.append(fitness)
            fuel_consumptions.append(fuel_consumption)

        best_sorted = sorted(zip(fitnesses, fuel_consumptions, population), key=lambda x: x[0], reverse=True)
        best_fitness, best_fuel_consumption, best_chromosome = best_sorted[0]
        print(f"Generation {generation}, "
              f"Best Fitness: {best_fitness}, "
              f"Fuel consumption: {best_fuel_consumption}, "
              f"Chromosome: {best_chromosome}")
        # for fitness, fuel_consumption, chromosome in best_sorted:
        #     print(fitness, fuel_consumption, chromosome)

        # Select the next generation
        new_population = []
        for _ in range(POPULATION_SIZE // 2):
            parent1 = random.choices(population, weights=fitnesses, k=1)[0]
            parent2 = random.choices(population, weights=fitnesses, k=1)[0]
            child1 = mutate(crossover(parent1, parent2), MUTATION_RATE)
            child2 = mutate(crossover(parent2, parent1), MUTATION_RATE)
            new_population.extend([child1, child2])

        population = new_population

    # Return the best solution
    best_chromosome = max(zip(population, fitnesses), key=lambda x: x[1])[0]
    return best_chromosome


def main() -> None:
    cdm1 = parse_cdm(Path("data/CSPOC_9.xml"))
    # cdm2 = parse_cdm(Path("data/CAESAR_TRJ_12.xml"))

    best_chromosome = genetic_algorithm(cdm1)
    print(f"Best Chromosome: {best_chromosome}")


if __name__ == "__main__":
    main()
