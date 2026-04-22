
from dataclasses import dataclass
from collections import Counter
import matplotlib.pyplot as plt
import numpy as np
import math
import csv

rng = np.random.default_rng(np.random.PCG64DXSM())

def rng_choice(seq):
    return seq[rng.integers(0, len(seq))]

def rng_random():
    return rng.random()

def rng_choices(seq, weights=None, k=1):
    seq = list(seq)
    if weights is not None:
        weights = np.array(weights, dtype=float)
        weights /= weights.sum()
        indices = rng.choice(len(seq), size=k, p=weights)
    else:
        indices = rng.integers(0, len(seq), size=k)
    return [seq[i] for i in indices]

def rng_randint(a, b):
    return int(rng.integers(a, b + 1))


faculty = ['Lock', 'Glen', 'Banks', 'Richards', 'Shaw', 'Singer', 'Uther', 'Tyler', 'Numen', 'Zeldin']
rooms = {'Beach 201': 18, 'Beach 301': 25, 'Frank 119': 95, 'Loft 206': 55, 'Loft 310': 48, 'James 325': 110, 'Roman 201': 40, 'Roman 216': 80, 'Slater 003': 32}
times = {10: '10AM', 11: '11AM', 12: '12PM', 13: '1PM', 14: '2PM', 15: '3PM'}
schedules = []
courses = []
printed_generations = []


violation_counts = [0, 0, 0, 0]  # [room conflict, facilitator overload, room size, special rules]


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


# Initializes the files
with open("violations.txt", "w", encoding="utf-8") as f:
    f.write("Violations Per Generation: \n\n")

with open("mutation_rate_history.txt", "w", encoding="utf-8") as f:
    f.write("Mutation Rate History: \n\n")

with open("generation_best_schedules.txt", "w", encoding="utf-8") as f:
    f.write("Best Schedule Per Generation: \n\n")

with open("fitness_history.csv", "w", encoding="utf-8") as f:
    f.write("Fitness History Per Generation: \n")
    f.write("Format: Generation,    Best fitness,   Avg fitness,    Worst fitness,  Improvement %\n\n")


def populate_courses():
    courses.append(Course('SLA101A', 40, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA101B', 35, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA191A', 45, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA191B', 40, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA201',  60, ['Glen', 'Banks', 'Zeldin', 'Lock', 'Singer'], ['Richards', 'Uther', 'Shaw']))
    courses.append(Course('SLA291',  50, ['Glen', 'Banks', 'Zeldin', 'Lock', 'Singer'], ['Richards', 'Uther', 'Shaw']))
    courses.append(Course('SLA303',  25, ['Glen', 'Zeldin'], ['Banks']))
    courses.append(Course('SLA304',  20, ['Singer', 'Uther'], ['Richards']))
    courses.append(Course('SLA394',  15, ['Tyler', 'Singer'], ['Richards', 'Zeldin']))
    courses.append(Course('SLA449',  30, ['Tyler', 'Zeldin', 'Uther'], ['Zeldin', 'Shaw']))
    courses.append(Course('SLA451',  90, ['Banks', 'Zeldin', 'Lock'], ['Tyler', 'Singer', 'Shaw', 'Glen']))

def make_individual():
    return [
        Schedule(
            course=c,
            faculty=rng_choice(faculty),
            room=rng_choice(list(rooms.keys())),
            time=rng_choice(list(times.keys())),
            fitness=0.0
        )
        for c in courses
    ]

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


# Determines a schedule's fitness
def fitness_function(individual, generation, count_violations=True):
    constraint_violations = []
    local_counts = [0, 0, 0, 0]  # local tally for this call

    faculty_count = Counter(s.faculty for s in individual)
    for schedule in individual:
        fitness = 0.00

        # overlapping rooms and times
        for i in range(len(individual)):
            if schedule.time == individual[i].time and schedule.room == individual[i].room and schedule != individual[i]:
                constraint_violations.append(f"     VIOLATION: Overlapping courses {schedule.course.name} and {individual[i].course.name} in room {schedule.room} at time {times[schedule.time]}")
                local_counts[0] += 1
                fitness -= 0.5

        # room size fitness
        if rooms[schedule.room] < schedule.course.enrollment:
            constraint_violations.append(f"     VIOLATION: Room {schedule.room} too small for {schedule.course.name} (enrollment {schedule.course.enrollment})")
            local_counts[2] += 1
            fitness -= 0.5
        elif rooms[schedule.room] > (schedule.course.enrollment * 3.00):
            constraint_violations.append(f"     VIOLATION: Room {schedule.room} too large for {schedule.course.name} (enrollment {schedule.course.enrollment})")
            local_counts[2] += 1
            fitness -= 0.4
        elif rooms[schedule.room] > (schedule.course.enrollment * 1.5):
            constraint_violations.append(f"     VIOLATION: Room {schedule.room} somewhat large for {schedule.course.name} (enrollment {schedule.course.enrollment})")
            local_counts[2] += 1
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
            local_counts[1] += 1
            fitness -= 0.2
        else:
            fitness += 0.2

        # faculty load — total count
        total = faculty_count[schedule.faculty]
        if total > 4:
            constraint_violations.append(f"     VIOLATION: Faculty {schedule.faculty} assigned to {total} courses (overload)")
            local_counts[1] += 1
            fitness -= 0.5
        elif schedule.faculty == 'Tyler' and total < 2:
            pass  # Tyler exception: no penalty for < 2 activities
        elif total < 3:
            constraint_violations.append(f"     VIOLATION: Faculty {schedule.faculty} assigned to only {total} courses (underload)")
            local_counts[1] += 1
            fitness -= 0.4

        # consecutive time check for a facilitator
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
                    local_counts[1] += 1
                    fitness -= 0.4

        schedule.fitness = fitness

    # Activity-based constraints
    sla101a = next((s for s in individual if s.course.name == 'SLA101A'), None)
    sla101b = next((s for s in individual if s.course.name == 'SLA101B'), None)
    sla191a = next((s for s in individual if s.course.name == 'SLA191A'), None)
    sla191b = next((s for s in individual if s.course.name == 'SLA191B'), None)

    if sla101a and sla101b:
        if abs(sla101a.time - sla101b.time) > 4:
            sla101a.fitness += 0.5
            sla101b.fitness += 0.5
        if sla101a.time == sla101b.time:
            constraint_violations.append(f"     VIOLATION: SLA101A and SLA101B scheduled at same time ({times[sla101a.time]})")
            local_counts[3] += 1
            sla101a.fitness -= 0.5
            sla101b.fitness -= 0.5

    if sla191a and sla191b:
        if abs(sla191a.time - sla191b.time) > 4:
            sla191a.fitness += 0.5
            sla191b.fitness += 0.5
        if sla191a.time == sla191b.time:
            constraint_violations.append(f"     VIOLATION: SLA191A and SLA191B scheduled at same time ({times[sla191a.time]})")
            local_counts[3] += 1
            sla191a.fitness -= 0.5
            sla191b.fitness -= 0.5

    group_101 = [sla101a, sla101b]
    group_191 = [sla191a, sla191b]

    for s101 in group_101:
        for s191 in group_191:
            if s101 and s191:
                diff = abs(s101.time - s191.time)
                if diff == 1:
                    s101.fitness += 0.5
                    s191.fitness += 0.5
                    complex_rooms = ['Roman', 'Beach']
                    s101_in = any(r in s101.room for r in complex_rooms)
                    s191_in = any(r in s191.room for r in complex_rooms)
                    if s101_in != s191_in:
                        constraint_violations.append(f"     VIOLATION: SLA101 and SLA191 scheduled back-to-back in different buildings ({s101.course.name} at {times[s101.time]} in {s101.room} and {s191.course.name} at {times[s191.time]} in {s191.room})")
                        local_counts[3] += 1
                        s101.fitness -= 0.4
                        s191.fitness -= 0.4
                elif diff == 2:
                    s101.fitness += 0.25
                    s191.fitness += 0.25
                elif diff == 0:
                    constraint_violations.append(f"     VIOLATION: SLA101 and SLA191 scheduled at same time ({times[s101.time]})")
                    local_counts[3] += 1
                    s101.fitness -= 0.25
                    s191.fitness -= 0.25

    # Counts the violations found in the schedule
    if count_violations:
        for i in range(4):
            violation_counts[i] += local_counts[i]

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
        if rng_random() < mutation_rate:
            target = rng_choice(['faculty', 'room', 'time'])
            if target == 'faculty':
                activity.faculty = rng_choice(faculty)
            elif target == 'room':
                activity.room = rng_choice(list(rooms.keys()))
            elif target == 'time':
                activity.time = rng_choice(list(times.keys()))


def selection(population, fitnesses):
    if len(population) == 0:
        return []
    if len(population) == 1:
        return [population[0], population[0]]

    max_fitness = max(fitnesses)
    exp_scores  = [math.exp(f - max_fitness) for f in fitnesses]
    total       = sum(exp_scores)

    if total == 0:
        return rng_choices(population, k=2)

    probabilities = [score / total for score in exp_scores]
    return rng_choices(population, weights=probabilities, k=2)


def crossover(population, fitnesses, offspring_count):
    if len(population) < 2:
        return []

    offspring = []
    while len(offspring) < offspring_count:
        parent1, parent2 = selection(population, fitnesses)
        point  = rng_randint(1, len(parent1) - 1)
        child1 = [Schedule(s.course, s.faculty, s.room, s.time, 0.0) for s in parent1[:point] + parent2[point:]]
        child2 = [Schedule(s.course, s.faculty, s.room, s.time, 0.0) for s in parent2[:point] + parent1[point:]]
        offspring.extend([child1, child2])

    return offspring[:offspring_count]


def reduce_population(population, fitnesses, keep_fraction=0.5):
    paired = sorted(zip(fitnesses, population), key=lambda x: x[0], reverse=True)
    keep_count = max(2, int(len(paired) * keep_fraction))
    fits, pops = zip(*paired[:keep_count])
    return list(pops), list(fits)


# Builds a formatted schedule block for a given timetable and fitness score
def format_schedule_block(generation, fitness, timetable):
    block  = f"Generation {generation} | Best fitness: {fitness:+.2f}\n"
    block += f"{'Course':<10} {'Faculty':<12} {'Room':<15} {'Time':<6} {'Fitness'}\n"
    block += "-" * 58 + "\n"
    for s in sorted(timetable, key=lambda x: x.time):
        block += f"{s.course.name:<10} {s.faculty:<12} {s.room:<15} {times[s.time]:<6} {s.fitness:+.2f}\n"
    block += "\n"
    return block


if __name__ == "__main__":
    populate_courses()
    population = generate_population(500)

    MIN_GENERATIONS = 100
    mutation_rate = 0.01
    best_overall = None
    best_fitness = float('-inf')
    prev_avg = None
    improvement = 0.00

    generations = []
    best_fitnesses = []
    average_fitnesses = []
    worst_fitnesses = []

    generation = 0
    print(f"\nRunning genetic algorithm (min {MIN_GENERATIONS} generations, stops when improvement < 1%)...")

    while True:
        generation += 1

        # 1. Score current population (counts violations, writes log)
        fitnesses = [fitness_function(ind, generation, count_violations=True) for ind in population]
        avg = sum(fitnesses) / len(fitnesses)

        # 2. Track best
        gen_best_idx = max(range(len(fitnesses)), key=lambda i: fitnesses[i])
        if fitnesses[gen_best_idx] > best_fitness:
            best_fitness = fitnesses[gen_best_idx]
            best_overall = (generation, [Schedule(s.course, s.faculty, s.room, s.time, s.fitness)
                                         for s in population[gen_best_idx]])

        # 3. Compute improvement and (if applicable) halve mutation rate
        if prev_avg is not None and prev_avg != 0:
            improvement = (avg - prev_avg) / abs(prev_avg)
            if improvement < 0.01:
                with open("mutation_rate_history.txt", "a") as f:
                    f.write(f"Generation: {generation}\n")
                    f.write(f"Improvement: {improvement:.6f}\n")
                    f.write(f"Previous mutation rate: {mutation_rate}\n")
                    mutation_rate = max(mutation_rate / 2, 1e-6)
                    f.write(f"New mutation rate: {mutation_rate}\n\n")

        prev_avg = avg

        # 4. Progress output
        gen_worst_idx = min(range(len(fitnesses)), key=lambda i: fitnesses[i])
        print(f"Generation {generation:3d} | Best: {fitnesses[gen_best_idx]:+.2f} | Avg: {avg:+.2f} | Worst: {fitnesses[gen_worst_idx]:+.2f} | Improvement: {improvement * 100:.2f}%")

        row = [generation, fitnesses[gen_best_idx], avg, fitnesses[gen_worst_idx], improvement * 100]
        with open("fitness_history.csv", "a") as f:
            writer = csv.writer(f)
            writer.writerow(row)

        generations.append(generation)
        best_fitnesses.append(fitnesses[gen_best_idx])
        average_fitnesses.append(avg)
        worst_fitnesses.append(fitnesses[gen_worst_idx])

        # Write this generation's best schedule to generation_best_schedules.txt
        with open("generation_best_schedules.txt", "a") as f:
            f.write(format_schedule_block(generation, fitnesses[gen_best_idx], population[gen_best_idx]))

        # Leaves the loop if generation 100 is reached AND the improvement is less than 1%
        if generation >= MIN_GENERATIONS and abs(improvement) < 0.01:
            print(f"\nStopping: improvement ({improvement*100:.4f}%) < 1% after {generation} generations.")
            break

        # 5. Breed offspring
        offspring = crossover(population, fitnesses, offspring_count=len(population))

        # 6. Mutate offspring
        for individual in offspring:
            mutation(individual, mutation_rate)

        # 7. Score offspring (do NOT count violations again — avoids double-counting)
        off_fitnesses = [fitness_function(ind, generation, count_violations=False) for ind in offspring]

        # 8. Combine and reduce
        population.extend(offspring)
        fitnesses.extend(off_fitnesses)
        population, fitnesses = reduce_population(population, fitnesses)

    # --- Final results ---
    gen_found, best_timetable = best_overall

    # Print sorted by time
    text = f"\n{'='*58}\n"
    text += f"OVERALL BEST (found in generation {gen_found}, total fitness {best_fitness:+.2f}):\n\n"
    text += f"--- Sorted by Time ---\n"
    text += f"{'Course':<10} {'Faculty':<12} {'Room':<15} {'Time':<6} {'Fitness'}\n"
    text += "-" * 58
    for s in sorted(best_timetable, key=lambda x: x.time):
        text += f"\n{s.course.name:<10} {s.faculty:<12} {s.room:<15} {times[s.time]:<6} {s.fitness:+.2f}"

    # Print sorted by activity name
    text += f"\n\n--- Sorted by Activity ---\n"
    text += f"{'Course':<10} {'Faculty':<12} {'Room':<15} {'Time':<6} {'Fitness'}\n"
    text += "-" * 58
    for s in sorted(best_timetable, key=lambda x: x.course.name):
        text += f"\n{s.course.name:<10} {s.faculty:<12} {s.room:<15} {times[s.time]:<6} {s.fitness:+.2f}"

    print(text)
    with open("generation_best_schedules.txt", "a") as f:
        f.write(text)


    # Linear fitness over generations
    plt.figure()
    plt.plot(generations, best_fitnesses,    label='Best',    color='green')
    plt.plot(generations, average_fitnesses, label='Average', color='blue')
    plt.plot(generations, worst_fitnesses,   label='Worst',   color='red')
    plt.title('Linear Fitness Over Generations')
    plt.xlabel('Generation')
    plt.ylabel('Fitness')
    plt.legend()

    # Creates the pie chart
    labels_all  = ['Room Conflicts', 'Faculty Overload', 'Room Size', 'Special Rules']
    filtered    = [(l, v) for l, v in zip(labels_all, violation_counts) if v > 0]
    if filtered:
        pie_labels, pie_values = zip(*filtered)
        fig_pie, ax_pie = plt.subplots()
        ax_pie.pie(pie_values, labels=pie_labels, autopct='%1.1f%%')
        ax_pie.set_title('Constraint Violations Breakdown')

    # Creates the bar chart
    faculty_counts = {f: 0 for f in faculty}
    for s in best_timetable:
        faculty_counts[s.faculty] += 1

    fig_bar, ax_bar = plt.subplots()
    ax_bar.bar(list(faculty_counts.keys()), list(faculty_counts.values()), color='tab:blue')
    ax_bar.set_ylabel('Number of Courses')
    ax_bar.set_title('Faculty Course Load (Best Schedule)')
    ax_bar.set_xlabel('Faculty')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()

    plt.show()