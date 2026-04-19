from dataclasses import dataclass
import random
import math

faculty = [
    "Lock",
    "Glen",
    "Banks",
    "Richards",
    "Shaw",
    "Singer",
    "Uther",
    "Tyler",
    "Numen",
    "Zeldin",
]
rooms = {
    "Beach 201": 18,
    "Beach 301": 25,
    "Frank 119": 95,
    "Loft 206": 55,
    "Loft 310": 48,
    "James 325": 110,
    "Roman 201": 40,
    "Roman 216": 80,
    "Slater 003": 32,
}
# courses = {'SLA101A': 40, 'SLA101B': 35, 'SLA191A': 45, 'SLA191B': 40, 'SLA201': 60, 'SLA291': 50, 'SLA303': 25, 'SLA304': 20, 'SLA394': 15, 'SLA449': 30, 'SLA451': 90}
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
    courses.append(
        Course(
            "SLA101A",
            40,
            ["Lock", "Glen", "Banks"],
            ["Numen", "Richards", "Shaw", "Singer"],
        )
    )
    courses.append(
        Course(
            "SLA101B",
            35,
            ["Lock", "Glen", "Banks"],
            ["Numen", "Richards", "Shaw", "Singer"],
        )
    )
    courses.append(
        Course(
            "SLA191A",
            45,
            ["Lock", "Glen", "Banks"],
            ["Numen", "Richards", "Shaw", "Singer"],
        )
    )
    courses.append(
        Course(
            "SLA191B",
            40,
            ["Lock", "Glen", "Banks"],
            ["Numen", "Richards", "Shaw", "Singer"],
        )
    )
    courses.append(
        Course(
            "SLA201",
            60,
            ["Glen", "Banks", "Zeldin", "Lock", "SInger"],
            ["Richards", "Uther", "Shaw"],
        )
    )
    courses.append(
        Course(
            "SLA291",
            50,
            ["Glen", "Banks", "Zeldin", "Lock", "SInger"],
            ["Richards", "Uther", "Shaw"],
        )
    )
    courses.append(Course("SLA303", 25, ["Glen", "Zeldin"], ["Banks"]))
    courses.append(Course("SLA304", 20, ["Singer", "Uther"], ["Richards"]))
    courses.append(Course("SLA394", 15, ["Singer", "Tyler"], ["Richards", "Zeldin"]))
    courses.append(
        Course("SLA449", 30, ["Tyler", "Zeldin", "Uther"], ["Zeldin", "Shaw"])
    )
    courses.append(
        Course(
            "SLA451",
            90,
            ["Banks", "Zeldin", "Lock"],
            ["Tyler", "Singer", "Shaw", "Glen"],
        )
    )


def generate_initial_schedules():
    for i in range(15):
        course = random.choice(courses)
        faculty_member = random.choice(faculty)
        room = random.choice(list(rooms.keys()))
        time = random.choice(times)
        fitness = 0.00
        schedules.append(Schedule(course, faculty_member, room, time, fitness))


def print_schedules():
    for i in range(len(schedules)):
        print(f"Schedule {i + 1} -")
        print(f"    Course: {schedules[i].course.name}")
        print(f"    Faculty: {schedules[i].faculty}")
        print(f"    Room: {schedules[i].room}")
        print(f"    Time: {schedules[i].time}")
        print(f"    Fitness: {schedules[i].fitness}\n\n")


# calculates the fitness of each schedule
def fitness_function(schedules):
    for schedule in schedules:
        fitness = 0.00

        # overlapping rooms and times
        for i in range(len(schedules)):
            if (
                schedule.time == schedules[i].time
                and schedule.room == schedules[i].room
                and schedule != schedules[i]
            ):  # checks for room conflicts
                fitness -= 0.5

        # room size fitness
        if rooms[schedule.room] < schedule.course.enrollment:
            fitness -= 0.5
        elif rooms[schedule.room] > (schedule.course.enrollment * 1.5):
            fitness -= 0.2
        elif rooms[schedule.room] > (schedule.course.enrollment * 3.00):
            fitness -= 0.4
        else:
            fitness += 0.3

        # faculty fitness
        if schedule.faculty in schedule.course.preferred_faculty:
            fitness += 0.5
        elif schedule.faculty in schedule.course.other_faculty:
            fitness += 0.2
        else:
            fitness -= 0.5

        # faculty load

        schedule.fitness = fitness
    pass


def mutation(population, mutation_rate):
    for individual_schedule in population:
        for activity in individual_schedule:
            
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
def selection(population=None):
    population = population if population is not None else schedules

    if len(population) == 0:
        return []
    if len(population) == 1:
        return [population[0], population[0]]

    fitness_values = [
        item.fitness if item.fitness is not None else 0.0 for item in population
    ]

    # Numerically stable softmax: exp(f_i - max_f)
    max_fitness = max(fitness_values)
    exp_scores = [math.exp(f - max_fitness) for f in fitness_values]
    total = sum(exp_scores)

    # If total underflows to 0 for any reason, fallback to uniform sampling.
    if total == 0:
        parent1 = random.choice(population)
        parent2 = random.choice(population)
        return [parent1, parent2]

    probabilities = [score / total for score in exp_scores]
    selected = random.choices(population, weights=probabilities, k=2)

    return selected


# creates the offspring between 2 schedules
def crossover(population=None, offspring_count=None):
    population = population if population is not None else schedules

    if len(population) < 2:
        return []

    target_offspring_count = (
        offspring_count if offspring_count is not None else len(population)
    )
    offspring = []

    while len(offspring) < target_offspring_count:
        parent1, parent2 = selection(population)

        child1 = Schedule(
            random.choice([parent1.course, parent2.course]),
            random.choice([parent1.faculty, parent2.faculty]),
            random.choice([parent1.room, parent2.room]),
            random.choice([parent1.time, parent2.time]),
            0.0,
        )

        child2 = Schedule(
            random.choice([parent1.course, parent2.course]),
            random.choice([parent1.faculty, parent2.faculty]),
            random.choice([parent1.room, parent2.room]),
            random.choice([parent1.time, parent2.time]),
            0.0,
        )

        offspring.extend([child1, child2])

    return offspring[:target_offspring_count]


# chooses which schedules to drop/remove
def reduce_population(population=None, keep_fraction=0.5):
    population = population if population is not None else schedules
    sorted_pop = sorted(
        population,
        key=lambda s: s.fitness if s.fitness is not None else 0.0,
        reverse=True,
    )
    keep_count = max(2, int(len(sorted_pop) * keep_fraction))
    return sorted_pop[:keep_count]


if __name__ == "__main__":
    populate_courses()
    generate_initial_schedules()
    fitness_function(schedules)
    print_schedules()
