from dataclasses import dataclass
from collections import Counter
import random
import math

faculty = [
    "Lock", "Glen", "Banks", "Richards", "Shaw",
    "Singer", "Uther", "Tyler", "Numen", "Zeldin",
]
rooms = {
    "Beach 201": 18, "Beach 301": 25, "Frank 119": 95,
    "Loft 206": 55,  "Loft 310": 48, "James 325": 110,
    "Roman 201": 40, "Roman 216": 80, "Slater 003": 32,
}
courses = []
times = ["10AM", "11AM", "12PM", "1PM", "2PM", "3PM"]
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


def populate_courses():
    courses.append(Course("SLA101A", 40, ["Lock", "Glen", "Banks"], ["Numen", "Richards", "Shaw", "Singer"]))
    courses.append(Course("SLA101B", 35, ["Lock", "Glen", "Banks"], ["Numen", "Richards", "Shaw", "Singer"]))
    courses.append(Course("SLA191A", 45, ["Lock", "Glen", "Banks"], ["Numen", "Richards", "Shaw", "Singer"]))
    courses.append(Course("SLA191B", 40, ["Lock", "Glen", "Banks"], ["Numen", "Richards", "Shaw", "Singer"]))
    courses.append(Course("SLA201",  60, ["Glen", "Banks", "Zeldin", "Lock", "Singer"], ["Richards", "Uther", "Shaw"]))  # fixed SInger
    courses.append(Course("SLA291",  50, ["Glen", "Banks", "Zeldin", "Lock", "Singer"], ["Richards", "Uther", "Shaw"]))  # fixed SInger
    courses.append(Course("SLA303",  25, ["Glen", "Zeldin"], ["Banks"]))
    courses.append(Course("SLA304",  20, ["Singer", "Uther"], ["Richards"]))
    courses.append(Course("SLA394",  15, ["Singer", "Tyler"], ["Richards", "Zeldin"]))
    courses.append(Course("SLA449",  30, ["Tyler", "Zeldin", "Uther"], ["Shaw"]))
    courses.append(Course("SLA451",  90, ["Banks", "Zeldin", "Lock"], ["Tyler", "Singer", "Shaw", "Glen"]))


def generate_initial_schedules():
    for i in range(250):
        schedules.append(Schedule(
            random.choice(courses),
            random.choice(faculty),
            random.choice(list(rooms.keys())),
            random.choice(times),
            0.00
        ))


def print_schedules():
    for i, s in enumerate(schedules):
        print(f"Schedule {i + 1} -")
        print(f"    Course:  {s.course.name}")
        print(f"    Faculty: {s.faculty}")
        print(f"    Room:    {s.room}")
        print(f"    Time:    {s.time}")
        print(f"    Fitness: {s.fitness}\n")


def fitness_function(schedules):
    time_slots = {
        "10AM": 0,
        "11AM": 1,
        "12PM": 2,
        "1PM": 3,
        "2PM": 4,
        "3PM": 5
    }

    faculty_count = Counter(s.faculty for s in schedules)

    for schedule in schedules:
        fitness = 0.00

        # overlapping rooms and times
        for other in schedules:
            if other is not schedule and schedule.time == other.time and schedule.room == other.room:
                fitness -= 0.5

        # room size fitness
        if rooms[schedule.room] < schedule.course.enrollment:
            fitness -= 0.5
        elif rooms[schedule.room] > (schedule.course.enrollment * 3.00):
            fitness -= 0.4
        elif rooms[schedule.room] > (schedule.course.enrollment * 1.5):
            fitness -= 0.2
        else:
            fitness += 0.3

        # faculty fitness
        if schedule.faculty in schedule.course.preferred_faculty:
            fitness += 0.5
        elif schedule.faculty in schedule.course.other_faculty:
            fitness += 0.2
        else:
            fitness -= 0.1

        # faculty same-time conflict
        same_time = sum(
            1 for s in schedules
            if s is not schedule and s.faculty == schedule.faculty and s.time == schedule.time
        )
        if same_time > 0:
            fitness -= 0.2
        else:
            fitness += 0.2

        # faculty total load
        total = faculty_count[schedule.faculty]

        if total > 4:
            fitness -= 0.5
        elif schedule.faculty == 'Tyler' and total < 2:
            pass
        elif total < 3:
            fitness -= 0.4

        # faculty spacing
        fac_times = [
            s.time for s in schedules
            if s.faculty == schedule.faculty and s is not schedule
        ]

        for other_time in fac_times:
            diff = abs(time_slots[schedule.time] - time_slots[other_time])

            if diff == 1:
                fitness -= 0.25
            elif diff == 2:
                fitness -= 0.25

        schedule.fitness = fitness

    sla101a = next((s for s in schedules if s.course.name == 'SLA101A'), None)
    sla101b = next((s for s in schedules if s.course.name == 'SLA101B'), None)
    sla191a = next((s for s in schedules if s.course.name == 'SLA191A'), None)
    sla191b = next((s for s in schedules if s.course.name == 'SLA191B'), None)

    if sla101a and sla101b:
        # 2 sections of SLA101 are more than 4 hrs apart
        if abs(time_slots[sla101a.time] - time_slots[sla101b.time]) > 4:
            sla101a.fitness += 0.5
            sla101b.fitness += 0.5

        # both sections of SLA101 are in same time slot
        if sla101a.time == sla101b.time:
            sla101a.fitness -= 0.5
            sla101b.fitness -= 0.5

    if sla191a and sla191b:
        # 2 sections of SLA191 are more than 4 hrs apart
        if abs(time_slots[sla191a.time] - time_slots[sla191b.time]) > 4:
            sla191a.fitness += 0.5
            sla191b.fitness += 0.5

        # both sections of SLA191 are in same time slot
        if sla191a.time == sla191b.time:
            sla191a.fitness -= 0.5
            sla191b.fitness -= 0.5

    group_101 = [sla101a, sla101b]
    group_191 = [sla191a, sla191b]

    for s101 in group_101:
        for s191 in group_191:
            if s101 and s191:
                diff = abs(time_slots[s101.time] - time_slots[s191.time])

                # SLA191 and SLA101 in consecutive time slot
                if diff == 1:
                    s101.fitness += 0.5
                    s191.fitness += 0.5

                    # building check
                    complex_rooms = ['Roman', 'Beach']
                    s101_in = any(r in s101.room for r in complex_rooms)
                    s191_in = any(r in s191.room for r in complex_rooms)

                    if s101_in != s191_in:
                        s101.fitness -= 0.4
                        s191.fitness -= 0.4

                # SLA191 and SLA101 separated by 1 hr
                elif diff == 2:
                    s101.fitness += 0.25
                    s191.fitness += 0.25

                # SLA191 and SLA101 are in same time slot
                elif diff == 0:
                    s101.fitness -= 0.25
                    s191.fitness -= 0.25

def mutation(population, mutation_rate):
    for schedule in population:
        if random.random() < mutation_rate:
            target = random.choice(['faculty', 'room', 'time'])
            if target == 'faculty':
                schedule.faculty = random.choice(faculty)
            elif target == 'room':
                schedule.room = random.choice(list(rooms.keys()))
            elif target == 'time':
                schedule.time = random.choice(times)
    return population


def selection(population):
    if len(population) == 0:
        return []
    if len(population) == 1:
        return [population[0], population[0]]

    fitness_values = [s.fitness for s in population]
    max_fitness = max(fitness_values)
    exp_scores  = [math.exp(f - max_fitness) for f in fitness_values]
    total       = sum(exp_scores)

    if total == 0:
        return random.choices(population, k=2)

    probabilities = [score / total for score in exp_scores]
    return random.choices(population, weights=probabilities, k=2)


def crossover(population, offspring_count):
    if len(population) < 2:
        return []

    offspring = []
    while len(offspring) < offspring_count:
        parent1, parent2 = selection(population)

        child1 = Schedule(
            random.choice([parent1.course,  parent2.course]),
            random.choice([parent1.faculty, parent2.faculty]),
            random.choice([parent1.room,    parent2.room]),
            random.choice([parent1.time,    parent2.time]),
            0.0,
        )
        child2 = Schedule(
            random.choice([parent1.course,  parent2.course]),
            random.choice([parent1.faculty, parent2.faculty]),
            random.choice([parent1.room,    parent2.room]),
            random.choice([parent1.time,    parent2.time]),
            0.0,
        )
        offspring.extend([child1, child2])

    return offspring[:offspring_count]


def reduce_population(population, keep_fraction=0.5):
    sorted_pop = sorted(population, key=lambda s: s.fitness, reverse=True)
    keep_count = max(2, int(len(sorted_pop) * keep_fraction))
    return sorted_pop[:keep_count]


if __name__ == "__main__":
    populate_courses()
    generate_initial_schedules()

    num_generations = 100
    mutation_rate   = 0.01
    best_per_gen    = []

    print(f"Running genetic algorithm for {num_generations} generations")

    for generation in range(num_generations):
        # 1. score current population
        fitness_function(schedules)

        # 2. track best
        best = max(schedules, key=lambda s: s.fitness)
        best_per_gen.append({'generation': generation + 1, 'schedule': best, 'fitness': best.fitness})

        # 3. progress every 10 gens
        if (generation + 1) % 10 == 0:
            avg = sum(s.fitness for s in schedules) / len(schedules)
            print(f"Generation {generation + 1:3d} | Best: {best.fitness:+.2f} | Avg: {avg:+.2f}")

        # 4. breed offspring
        offspring = crossover(schedules, offspring_count=len(schedules))

        # 5. mutate — pass offspring directly, NOT wrapped in a list
        mutation(offspring, mutation_rate)

        # 6. score offspring
        fitness_function(offspring)

        # 7. combine and reduce
        schedules.extend(offspring)
        schedules[:] = reduce_population(schedules, keep_fraction=0.5)

    # final results
    overall_best = max(best_per_gen, key=lambda x: x['fitness'])

    print(f"\nBest found in Generation {overall_best['generation']}:")
    print(f"  Course:  {overall_best['schedule'].course.name}")
    print(f"  Faculty: {overall_best['schedule'].faculty}")
    print(f"  Room:    {overall_best['schedule'].room}")
    print(f"  Time:    {overall_best['schedule'].time}")
    print(f"  Fitness: {overall_best['fitness']:+.2f}")

    print("\nTOP 10 SCHEDULES FROM FINAL POPULATION")
    top10 = sorted(schedules, key=lambda s: s.fitness, reverse=True)[:10]
    for i, s in enumerate(top10, 1):
        print(f"\n{i}. {s.course.name} | {s.faculty} | {s.room} | {s.time} | Fitness: {s.fitness:+.2f}")