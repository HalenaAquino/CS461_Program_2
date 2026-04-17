from dataclasses import dataclass
from collections import Counter
import  random

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


def populate_courses():
    courses.append(Course('SLA101A', 40, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA101B', 35, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA191A', 45, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA191B', 40, ['Lock', 'Glen', 'Banks'], ['Numen', 'Richards', 'Shaw', 'Singer']))
    courses.append(Course('SLA201', 60, ['Glen', 'Banks', 'Zeldin', 'Lock', 'Singer'], ['Richards', 'Uther', 'Shaw']))
    courses.append(Course('SLA291', 50, ['Glen', 'Banks', 'Zeldin', 'Lock', 'Singer'], ['Richards', 'Uther', 'Shaw']))
    courses.append(Course('SLA303', 25, ['Glen', 'Zeldin'], ['Banks']))
    courses.append(Course('SLA304', 20, ['Singer', 'Uther'], ['Richards']))
    courses.append(Course('SLA394', 15, ['Singer', 'Tyler'], ['Richards', 'Zeldin']))
    courses.append(Course('SLA449', 30, ['Tyler', 'Zeldin', 'Uther'], ['Zeldin', 'Shaw']))
    courses.append(Course('SLA451', 90, ['Banks', 'Zeldin', 'Lock'], ['Tyler', 'Singer', 'Shaw', 'Glen']))
    
def generate_initial_schedules():
    for i in range(15):
        course = random.choice(courses)
        faculty_member = random.choice(faculty)
        room = random.choice(list(rooms.keys()))
        time = random.choice(list(times.keys()))
        fitness = 0.00
        schedules.append(Schedule(course, faculty_member, room, time, fitness))

def print_schedules():
    for i in range(len(schedules)):
        print(f'Schedule {i+1} -')
        print(f'    Course: {schedules[i].course.name}')
        print(f'    Faculty: {schedules[i].faculty}')
        print(f'    Room: {schedules[i].room}')
        print(f'    Time: {times[schedules[i].time]}')
        print(f'    Fitness: {schedules[i].fitness}\n\n')
        s = schedules[i]

# calculates the fitness of each schedule
def fitness_function(schedules):
    faculty_count = Counter(s.faculty for s in schedules)
    for schedule in schedules:
        fitness = 0.00 

        # overlapping rooms and times
        for i in range(len(schedules)):
            if schedule.time == schedules[i].time and schedule.room == schedules[i].room and schedule != schedules[i]: # checks for room conflicts
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


        # faculty load
        same_time = sum(
            1 for s in schedules
            if s is not schedule and s.faculty == schedule.faculty and s.time == schedule.time
        )
        if same_time > 0:
            fitness -= 0.2
        else:
            fitness += 0.2

        total = faculty_count[schedule.faculty]

        if total > 4:
            fitness -= 0.5
        elif schedule.faculty == 'Tyler' and total < 2:
            pass
        elif total < 3:
            fitness -= 0.4


        fac_times = sorted(
            (s.time for s in schedules if s.faculty == schedule.faculty and s is not schedule)
        )

        for time in fac_times:
            diff = abs(schedule.time - time)

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
        #  2 sections of SLA101 are more than 4 hrs apart
        if abs(sla101a.time - sla101b.time) > 4:
            sla101a.fitness += 0.5
            sla101b.fitness += 0.5
        # both sections of SLA101 are in same time slot
        if sla101a.time == sla101b.time:
            sla101a.fitness -= 0.5
            sla101b.fitness -= 0.5
    
    if sla191a and sla191b:
        # 2 sections of SLA191 are more than 4 hrs apart
        if abs(sla191a.time - sla191b.time) > 4:
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
                        s101.fitness -= 0.4
                        s191.fitness -= 0.4
                
                # SLA191 and SLA101 separated by 1 hr 
                elif diff == 2:
                    s101.fitness += 0.25
                    s191.fitness += 0.25
                
                # SLA 191 and SLA 101 are in same time slot
                elif diff == 0:
                    s101.fitness -= 0.25
                    s191.fitness -= 0.25


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
def selection():
    pass

# creates the offspring between 2 schedules
def crossover():
    reduce_population() # removes the weak schedules before reproducing
    pass

# chooses which schedules to drop/remove
def reduce_population(): 
    pass

if __name__ == "__main__":
    populate_courses()

    generate_initial_schedules()

    fitness_function(schedules)
    print_schedules()