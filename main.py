# TODO:
# - Fix mutation rate write to file
# - Add a bar chart for course load
# - Add a pie chart for room utilization or total conflicts 




from dataclasses import dataclass
from collections import Counter
import matplotlib.pyplot as plt
import  random
import math
import csv

faculty = ['Lock', 'Glen', 'Banks', 'Richards', 'Shaw', 'Singer', 'Uther', 'Tyler', 'Numen', 'Zeldin']
rooms = {'Beach 201': 18, 'Beach 301': 25, 'Frank 119': 95, 'Loft 206': 55, 'Loft 310': 48, 'James 325': 110, 'Roman 201': 40, 'Roman 216': 80, 'Slater 003': 32}
courses = []
times = {10: '10AM', 11: '11AM', 12: '12PM', 13: '1PM', 14: '2PM', 15: '3PM'}
schedules = []

@dataclass 
class Course:
    name: str
    enrollment: int
    preferred_faculty: list
    other_faculty: list


@dataclass 
class Schedule:
    course: Course
    faculty: str
    room: str
    time: str
    fitness: float


with open("violations.txt", "w", encoding="utf-8") as f:
    f.write("Violations Per Generation: \n\n")

with open("mutation_rate_history.txt", "w", encoding="utf-8") as f:
    f.write("Mutation Rate History: \n\n")

with open("final_best_schedule.txt", "w", encoding="utf-8") as f:
    f.write("Final Best Schedule: \n\n")

with open("fitness_history.csv", "w", encoding="utf-8") as f:
    f.write("Fitness History Per Generation: \n")
    f.write("Format: Generation,    Best fitness,   Avg fitness,    Worst fitness,  Improvement %\n\n")


def populate_courses():
    courses.append(Course('SLA101A', 40, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA101B', 35, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA191A', 45, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA191B', 40, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA201', 60, ['Glen', 'Banks', 'Zeldin', 'Lock', 'Singer'], ['Richards', 'Uther', 'Shaw']))
    courses.append(Course('SLA291', 50, ['Glen', 'Banks', 'Zeldin', 'Lock', 'Singer'], ['Richards', 'Uther', 'Shaw']))
    courses.append(Course('SLA303', 25, ['Glen', 'Zeldin'], ['Banks']))
    courses.append(Course('SLA304', 20, ['Singer', 'Uther'], ['Richards']))
    courses.append(Course('SLA394', 15, ['Tyler', 'Singer'], ['Richards', 'Zeldin']))
    courses.append(Course('SLA449', 30, ['Tyler', 'Zeldin', 'Uther'], ['Zeldin', 'Shaw']))
    courses.append(Course('SLA451', 90, ['Banks', 'Zeldin', 'Lock'], ['Tyler', 'Singer', 'Shaw', 'Glen']))
    
# makes each individual schedules
def make_individual():
    return [
        Schedule(
            course=c,
            faculty=random.choice(faculty),
            room=random.choice(list(rooms.keys())),
            time=random.choice(list(times.keys())),
            fitness=0.0
        )
        for c in courses
    ]

# generates the initial schedule population
def generate_population(size=250):
    return [make_individual() for _ in range(size)]

def print_schedules():
    for i, s in enumerate(schedules):
        print(f"Schedule {i + 1} -")
        print(f"    Course:  {s.course.name}")
        print(f"    Faculty: {s.faculty}")
        print(f"    Room:    {s.room}")
        print(f"    Time:    {s.time}")
        print(f"    Fitness: {s.fitness}\n")

printed_generations = []


# calculates the fitness of each schedule
def fitness_function(individual, generation):
    constraint_violations = []
    
    faculty_count = Counter(s.faculty for s in individual)
    for schedule in individual:
        fitness = 0.00 

        # overlapping rooms and times
        for i in range(len(individual)):
            if schedule.time == individual[i].time and schedule.room == individual[i].room and schedule != individual[i]: # checks for room conflicts
                constraint_violations.append(f"       VIOLATION: Overlapping courses {schedule.course.name} and {individual[i].course.name} in room {schedule.room} at time {times[schedule.time]}")
                fitness -= 0.5

        # room size fitness
        if rooms[schedule.room] < schedule.course.enrollment:
            constraint_violations.append(f"     VIOLATION: Room {schedule.room} too small for {schedule.course.name} (enrollment {schedule.course.enrollment})")
            fitness -= 0.5
        elif rooms[schedule.room] > (schedule.course.enrollment * 3.00):
            constraint_violations.append(f"     VIOLATION: Room {schedule.room} too large for {schedule.course.name} (enrollment {schedule.course.enrollment})")    
            fitness -= 0.4
        elif rooms[schedule.room] > (schedule.course.enrollment * 1.5):
            constraint_violations.append(f"     VIOLATION: Room {schedule.room} somewhat large for {schedule.course.name} (enrollment {schedule.course.enrollment})")
            fitness -= 0.2
        else:
            fitness += 0.3


        # faculty fitness
        if schedule.faculty in schedule.course.preferred_faculty:
            fitness += 0.5
        elif schedule.faculty in schedule.course.other_faculty:
            fitness += 0.2
        else:
            constraint_violations.append(f"     VIOLATION: Faculty {schedule.faculty} not qualified to teach {schedule.course.name}")
            fitness -= 0.1

        # faculty load
        same_time = sum(
            1 for s in individual
            if s is not schedule and s.faculty == schedule.faculty and s.time == schedule.time
        )
        if same_time > 0:
            constraint_violations.append(f"     VIOLATION: Faculty {schedule.faculty} has multiple courses at {times[schedule.time]}")
            fitness -= 0.2
        else:
            fitness += 0.2

        total = faculty_count[schedule.faculty]

        if total > 4:
            constraint_violations.append(f"     VIOLATION: Faculty {schedule.faculty} assigned to {total} courses (overload)")
            fitness -= 0.5
        elif schedule.faculty == 'Tyler' and total < 2:
            pass
        elif total < 3:
            constraint_violations.append(f"     VIOLATION: Faculty {schedule.faculty} assigned to only {total} courses (underload)")
            fitness -= 0.4

        fac_schedules = [s for s in individual if s.faculty == schedule.faculty and s is not schedule]

        for other in fac_schedules:
            diff = abs(schedule.time - other.time)

            if diff == 1:
                fitness += 0.5

                complex_rooms = ['Roman', 'Beach']
                this_in  = any(r in schedule.room for r in complex_rooms)
                other_in = any(r in other.room for r in complex_rooms)

                if this_in != other_in:
                    constraint_violations.append(f"     VIOLATION: Faculty {schedule.faculty} has back-to-back courses in different buildings ({schedule.course.name} at {times[schedule.time]} in {schedule.room} and {other.course.name} at {times[other.time]} in {other.room})")
                    fitness -= 0.4

        schedule.fitness = fitness

    sla101a = next((s for s in individual if s.course.name == 'SLA101A'), None)
    sla101b = next((s for s in individual if s.course.name == 'SLA101B'), None)
    sla191a = next((s for s in individual if s.course.name == 'SLA191A'), None)
    sla191b = next((s for s in individual if s.course.name == 'SLA191B'), None)

    if sla101a and sla101b:
        #  2 sections of SLA101 are more than 4 hrs apart
        if abs(sla101a.time - sla101b.time) > 4:
            sla101a.fitness += 0.5
            sla101b.fitness += 0.5
        # both sections of SLA101 are in same time slot
        if sla101a.time == sla101b.time:
            constraint_violations.append(f"     VIOLATION: SLA101A and SLA101B scheduled at same time ({times[sla101a.time]})")
            sla101a.fitness -= 0.5
            sla101b.fitness -= 0.5
    
    if sla191a and sla191b:
        # 2 sections of SLA191 are more than 4 hrs apart
        if abs(sla191a.time - sla191b.time) > 4:
            sla191a.fitness += 0.5
            sla191b.fitness += 0.5
        # both sections of SLA191 are in same time slot
        if sla191a.time == sla191b.time:
            constraint_violations.append(f"     VIOLATION: SLA191A and SLA191B scheduled at same time ({times[sla191a.time]})")
            sla191a.fitness -= 0.5
            sla191b.fitness -= 0.5
    
    group_101 = [sla101a, sla101b]
    group_191 = [sla191a, sla191b]

    for s101 in group_101:
        for s191 in group_191:
            if s101 and s191:
                diff = abs(s101.time - s191.time)
                
                # SLA191 and SLA101 in consecutive time slot
                if diff == 1:
                    s101.fitness += 0.5
                    s191.fitness += 0.5
                    # building check
                    complex_rooms = ['Roman', 'Beach']
                    s101_in = any(r in s101.room for r in complex_rooms)
                    s191_in = any(r in s191.room for r in complex_rooms)
                    
                    if s101_in != s191_in:
                        constraint_violations.append(f"     VIOLATION: SLA101 and SLA191 scheduled back-to-back in different buildings ({s101.course.name} at {times[s101.time]} in {s101.room} and {s191.course.name} at {times[s191.time]} in {s191.room})")
                        s101.fitness -= 0.4
                        s191.fitness -= 0.4
                
                # SLA191 and SLA101 separated by 1 hr 
                elif diff == 2:
                    s101.fitness += 0.25
                    s191.fitness += 0.25
                
                # SLA 191 and SLA 101 are in same time slot
                elif diff == 0:
                    constraint_violations.append(f"     VIOLATION: SLA101 and SLA191 scheduled at same time ({times[s101.time]})")
                    s101.fitness -= 0.25
                    s191.fitness -= 0.25


    # Prints all violations to violations.txt
    if generation not in printed_generations:
        printed_generations.append(generation)
        with open("violations.txt", "a") as f:
            f.write(f"Generation {generation}:\n")
            for v in constraint_violations:
                f.write(v + "\n")
            f.write("\n")

    return sum(s.fitness for s in individual)

def mutation(population, mutation_rate=0.01):
    for activity in population:
        
        if random.random() < mutation_rate:
            # randomly choose which attrib to mutate
            target = random.choice(['faculty','room','time'])
            
            if target == 'faculty':
                activity.faculty = random.choice(faculty)
            elif target == 'room':
                activity.room = random.choice(list(rooms.keys()))
            elif target == 'time':
                activity.time = random.choice(list(times.keys()))

# selects the best schedules to be used for crossover
def selection(population, fitnesses):
    if len(population) == 0:
        return []
    if len(population) == 1:
        return [population[0], population[0]]

    max_fitness = max(fitnesses)
    exp_scores  = [math.exp(f - max_fitness) for f in fitnesses]
    total       = sum(exp_scores)

    if total == 0:
        return random.choices(population, k=2)

    probabilities = [score / total for score in exp_scores]
    return random.choices(population, weights=probabilities, k=2)

# creates the offspring between 2 schedules
def crossover(population, fitnesses, offspring_count):
    if len(population) < 2:
        return []

    offspring = []
    while len(offspring) < offspring_count:
        parent1, parent2 = selection(population, fitnesses)

        point = random.randint(1, len(parent1) - 1)
        child1 = [Schedule(s.course, s.faculty, s.room, s.time, 0.0) for s in parent1[:point] + parent2[point:]]
        child2 = [Schedule(s.course, s.faculty, s.room, s.time, 0.0) for s in parent2[:point] + parent1[point:]]
        offspring.extend([child1, child2])

    return offspring[:offspring_count]

# chooses which schedules to drop/remove
def reduce_population(population, fitnesses, keep_fraction=0.5): 
    paired = sorted(zip(fitnesses, population), key=lambda x: x[0], reverse=True)
    keep_count = max(2, int(len(paired) * keep_fraction))
    fits, pops = zip(*paired[:keep_count])
    return list(pops), list(fits)

generations = []
best_fitnesses = []
average_fitnesses = []
worst_fitnesses = []


if __name__ == "__main__":
    populate_courses()
    population = generate_population(250)

    num_generations = 100
    mutation_rate   = 0.01
    best_overall    = None
    best_fitness    = float('-inf')
    prev_avg = None
    improvement = 0.00

    print(f"\nRunning genetic algorithm for {num_generations} generations...")

    for generation in range(num_generations):
        # 1. score current population
        fitnesses = [fitness_function(ind, generation+1) for ind in population]
        avg = sum(fitnesses) / len(fitnesses)

        # 2. track best
        gen_best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
        if fitnesses[gen_best_idx] > best_fitness:
            best_fitness = fitnesses[gen_best_idx]
            best_overall = (generation + 1, [Schedule(s.course, s.faculty, s.room, s.time, s.fitness)
                                              for s in population[gen_best_idx]])

        # if the improvement is < 1%, halves it
        if prev_avg is not None and prev_avg != 0:
            improvement = (avg - prev_avg) / abs(prev_avg)
            if improvement < 0.01:  # less than 1% improvement
                # Prints the mutation rate to the file
                with open("mutation_rate_history.txt", "a") as f:
                    f.write(f"Generation: {generation+1}\n")
                    f.write(f"Mutation rate improvement: {improvement}\n")
                    f.write(f"Previous mutation rate: {mutation_rate}\n")
                    mutation_rate = max(mutation_rate / 2, 1e-6)
                    f.write(f"New mutation rate: {mutation_rate}\n\n")

        prev_avg = avg

        # 3. progress every 10 gens
        #if (generation + 1) % 10 == 0:
        avg = sum(fitnesses) / len(fitnesses)
        gen_worst_idx = min(range(len(fitnesses)), key=lambda i: fitnesses[i])
        print(f"Generation {generation + 1:3d} | Best: {fitnesses[gen_best_idx]:+.2f} | Avg: {avg:+.2f} | Worst: {fitnesses[gen_worst_idx]:+.2f} | Improvement: {improvement * 100:.2f}%")
        
        row = [generation + 1, fitnesses[gen_best_idx], avg, fitnesses[gen_worst_idx], improvement * 100]

        with open("fitness_history.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        # 4. breed offspring
        offspring = crossover(population, fitnesses, offspring_count=len(population))


        # 5. mutate
        for individual in offspring:
            mutation(individual, mutation_rate)

        # 6. score offspring
        off_fitnesses = [fitness_function(ind, generation+1) for ind in offspring]

        # 7. combine and reduce
        population.extend(offspring)
        fitnesses.extend(off_fitnesses)
        population, fitnesses = reduce_population(population, fitnesses)

        generations.append(generation + 1)
        best_fitnesses.append(fitnesses[gen_best_idx])
        average_fitnesses.append(avg)
        worst_fitnesses.append(fitnesses[gen_worst_idx])



    # final results
    gen_found, best_timetable = best_overall

    with open("final_best_schedule.txt", "a") as f:
        print(f"\nBest complete timetable (found in generation {gen_found}, total fitness {best_fitness:+.2f}):")
        print(f"{'Course':<10} {'Faculty':<12} {'Room':<15} {'Time':<6} {'Fitness'}")
        print("-" * 58)

        f.write(f"\nBest complete timetable (found in generation {gen_found}, total fitness {best_fitness:+.2f}):\n")
        f.write(f"{'Course':<10} {'Faculty':<12} {'Room':<15} {'Time':<6} {'Fitness'}\n")
        f.write("-" * 58)
        f.write("\n")
        for s in sorted(best_timetable, key=lambda x: x.time):
            f.write(f"{s.course.name:<10} {s.faculty:<12} {s.room:<15} {times[s.time]:<6} {s.fitness:+.2f} \n")
            print(f"{s.course.name:<10} {s.faculty:<12} {s.room:<15} {times[s.time]:<6} {s.fitness:+.2f}")


    # Creates the fitness chart
    plt.plot(generations, best_fitnesses, label='Best', color='green', linestyle='-')
    plt.plot(generations, average_fitnesses, label='Average', color='blue', linestyle='-')
    plt.plot(generations, worst_fitnesses, label='Worst', color='red', linestyle='-')

    # Add formatting
    plt.title('Linear Fitness Over Generations')
    plt.xlabel('Generations')
    plt.ylabel('Linear Fitness')
    plt.legend()
    plt.show()