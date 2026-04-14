from dataclasses import dataclass
import  random

faculty = ['Lock', 'Glen', 'Banks', 'Richards', 'Shaw', 'Singer', 'Uther', 'Tyler', 'Numen', 'Zeldin']
rooms = {'Beach 201': 18, 'Beach 301': 25, 'Frank 119': 95, 'Loft 206': 55, 'Loft 310': 48, 'James 325': 110, 'Roman 201': 40, 'Roman 216': 80, 'Slater 003': 32}
#courses = {'SLA101A': 40, 'SLA101B': 35, 'SLA191A': 45, 'SLA191B': 40, 'SLA201': 60, 'SLA291': 50, 'SLA303': 25, 'SLA304': 20, 'SLA394': 15, 'SLA449': 30, 'SLA451': 90}
courses = []
times = ['10AM', '11AM', '12PM', '1PM', '2PM', '3PM']
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
    courses.append(Course('SLA101A', 40, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA101B', 35, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA191A', 45, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA191B', 40, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA201', 60, ['Glen', 'Banks', 'Zeldin', 'Lock', 'SInger'], ['Richards', 'Uther', 'Shaw']))
    courses.append(Course('SLA291', 50, ['Glen', 'Banks', 'Zeldin', 'Lock', 'SInger'], ['Richards', 'Uther', 'Shaw']))
    courses.append(Course('SLA303', 25, ['Glen', 'Zeldin'], ['Banks']))
    courses.append(Course('SLA304', 20, ['Singer', 'Uther'], ['Richards']))
    courses.append(Course('SLA394', 15, ['Singer', 'Tyler'], ['Richards', 'Zeldin']))
    courses.append(Course('SLA449', 30, ['Tyler', 'Zeldin', 'Uther'], ['Zeldin', 'Shaw']))
    courses.append(Course('SLA451', 90, ['Banks', 'Zeldin', 'Lock'], ['Tyler', 'Singer', 'Shaw', 'Glen']))
    

def generate_initial_schedules():
    for i in range(250):
        course = random.choice(courses).name
        faculty_member = random.choice(faculty)
        room = random.choice(list(rooms.keys()))
        time = random.choice(times)
        fitness = 0.00
        schedules.append(Schedule(course, faculty_member, room, time, fitness))

def print_schedules():
    for i in range(len(schedules)):
        print(f'Schedule {i+1} -')
        print(f'    Course: {schedules[i].course}')
        print(f'    Faculty: {schedules[i].faculty}')
        print(f'    Room: {schedules[i].room}')
        print(f'    Time: {schedules[i].time}')
        print(f'    Fitness: {schedules[i].fitness}\n\n')
        s = schedules[i]

# calculates the fitness of each schedule
def fitness_function():
    pass

def mutation():
    pass

# selects the best schedules to be used for crossover
def selection():
    pass

# creates the offspring between 2 schedules
def crossover():
    pass


if __name__ == "__main__":
    populate_courses()
    generate_initial_schedules()
    print_schedules()
