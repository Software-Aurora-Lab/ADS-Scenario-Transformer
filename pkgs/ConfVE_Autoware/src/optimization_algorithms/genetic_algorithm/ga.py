import random
from copy import deepcopy
from src.config import SELECT_NUM_RATIO, SELECT_MODE, POP_SIZE, CX_P, MUT_P
from optimization_algorithms.genetic_algorithm.IndividualWithFitness import IndividualWithFitness
from optimization_algorithms.genetic_algorithm.nsga2 import sort_nondominated, crowding_dist


def generate_individuals(config_file_obj, population_size):
    generated_value_lists = list()
    for i in range(population_size):
        generated_value_list = list()
        for option_value in config_file_obj.default_option_value_list:
            generated_value = option_value
            generated_value_list.append(generated_value)
        generated_value_lists.append(generated_value_list)
    individual_list = [IndividualWithFitness(value_list) for value_list in generated_value_lists]
    return individual_list


def select(individual_list, config_file_obj):
    individual_list = [item for item in individual_list if item.allow_selection]

    if SELECT_MODE == "nsga2":
        fitness_list = [individual.fitness for individual in individual_list]
        fronts_index_list = sort_nondominated(fitness_list)
        distances_list = crowding_dist(fitness_list)

        select_counter = 0
        selected_index_list = []
        for sub_fronts_list in fronts_index_list:
            if select_counter + len(sub_fronts_list) < POP_SIZE:
                selected_index_list += sub_fronts_list
                select_counter += len(sub_fronts_list)
            else:
                sub_indexed_distances = [(index, distances_list[index]) for index in sub_fronts_list]
                sub_indexed_distances.sort(reverse=True, key=lambda x: x[1])
                sub_select_num = POP_SIZE - select_counter
                for index, distance in sub_indexed_distances[:sub_select_num]:
                    selected_index_list.append(index)
                break

        optimal_individual_list = [individual_list[index] for index in selected_index_list]
        new_individual_list = optimal_individual_list
    else:
        individual_list.sort(reverse=True, key=lambda x: x.fitness)
        select_num_ratio = SELECT_NUM_RATIO
        new_individual_list = get_unduplicated(individual_list, select_num_ratio, config_file_obj)
    return new_individual_list


def get_unduplicated(individual_list, select_num_ratio, config_file_obj):
    individuals_with_least_fitness = individual_list[:select_num_ratio[0]]
    individuals_from_remaining = random.choices(individual_list[select_num_ratio[0]:], k=select_num_ratio[1])
    individuals_new_generated = generate_individuals(config_file_obj, select_num_ratio[2])
    selected_individuals_list = individuals_with_least_fitness + individuals_from_remaining + individuals_new_generated
    return selected_individuals_list


def crossover(individual_list):
    individual_list_size = len(individual_list)
    randa = random.randint(0, individual_list_size - 1)
    randb = random.randint(0, individual_list_size - 1)
    while randb == randa:
        randb = random.randint(0, individual_list_size - 1)
    individual_A = deepcopy(individual_list[randa])
    individual_B = deepcopy(individual_list[randb])

    individual_A.pre_value_list = deepcopy(individual_A.value_list)
    individual_B.pre_value_list = deepcopy(individual_B.value_list)

    position = random.randint(1, len(individual_list[0].value_list) - 1)
    individual_A.value_list = individual_list[randa].value_list[:position] + individual_list[randb].value_list[
                                                                             position:]
    individual_B.value_list = individual_list[randb].value_list[:position] + individual_list[randa].value_list[
                                                                             position:]

    individual_A.option_tuning_tracking_list.append("crossover")
    individual_B.option_tuning_tracking_list.append("crossover")
    return individual_A, individual_B


def mutate(individual, config_file_obj, range_analyzer):
    tuned_id = random.randint(0, len(individual.value_list) - 1)
    range_analyzer.tune_one_value(individual, config_file_obj, tuned_id)
    return individual

def init_mutation(individual_list, config_file_obj, range_analyzer):
    new_individual_list = []
    for individual in individual_list:
        new_individual = mutate(individual, config_file_obj, range_analyzer)
        new_individual_list.append(new_individual)
    return new_individual_list

def mutation(individual_list, config_file_obj, range_analyzer):
    individual = random.choice(individual_list)
    new_individual = mutate(deepcopy(individual), config_file_obj, range_analyzer)
    return new_individual

def ga_operation(individual_list, config_file_obj, range_analyzer):
    offspring = []
    for _ in range(POP_SIZE):
        op_choice = random.random()
        if op_choice < CX_P:            # Apply crossover
            individual_A, individual_B = crossover(individual_list)
            individual_A.reset_default()
            offspring.append(individual_A)
        elif op_choice < CX_P + MUT_P:  # Apply mutation
            individual = random.choice(individual_list)
            new_individual = mutate(deepcopy(individual), config_file_obj, range_analyzer)
            new_individual.reset_default()
            offspring.append(new_individual)
        else:                           # Apply reproduction
            offspring.append(random.choice(individual_list))
    return offspring

