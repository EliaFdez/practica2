"""
Solution to the one-way tunnel.
Let cars in the tunnel depending on how many cars had passed together in each direction. Solve starvation problems.
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "south"
NORTH = "north"

NCARS = 25
K = 3

class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.south = Value('i', 0)  # number of cars in south direction
        self.north = Value('i', 0)  # number of cars in north direction
        self.waiting_south = Value('i', 0)  # number of cars waiting in south direction
        self.waiting_north = Value('i', 0)  # number of cars waiting in north direction
        self.had_passed_south = Value('i', 0)  # number of cars that had passed in south direction
        self.had_passed_north = Value('i', 0)  # number of cars that had passed in north direction
        self.no_south = Condition(self.mutex)
        self.no_north = Condition(self.mutex)

    def wants_enter(self, direction):
        self.mutex.acquire()

        if direction == NORTH:
            self.waiting_north.value += 1
            self.no_south.wait_for(lambda: self.south.value == 0 and (self.had_passed_north.value < K or self.waiting_south.value == 0))
            self.waiting_north.value -= 1
            self.had_passed_south.value = 0
            self.north.value += 1
            self.had_passed_north.value += 1
            print(f'{self.had_passed_north.value} cars had passed direction NORTH and {self.waiting_south.value} cars are waiting direction SOUTH\n')
        else:
            self.waiting_south.value += 1
            self.no_north.wait_for(lambda: self.north.value == 0 and (self.had_passed_south.value < K or self.waiting_north.value == 0))
            self.waiting_south.value -= 1
            self.had_passed_north.value = 0
            self.south.value += 1
            self.had_passed_south.value += 1
            print(f'{self.had_passed_south.value} cars had passed direction SOUTH and {self.waiting_north.value} cars are waiting direction NORTH\n')

        self.mutex.release()

    def leaves_tunnel(self, direction):
        self.mutex.acquire()

        if direction == NORTH:
            self.north.value -= 1
            self.no_north.notify_all()
        else:
            self.south.value -= 1
            self.no_south.notify_all()

        self.mutex.release()


def delay(n=3):
    time.sleep(random.random() * n)


def car(cid, direction, monitor):
    print(f"car {cid} direction {direction} created")
    delay(6)
    print(f"car {cid} heading {direction} wants to enter")
    monitor.wants_enter(direction)
    print(f"car {cid} heading {direction} enters the tunnel")
    delay(3)
    print(f"car {cid} heading {direction} leaving the tunnel")
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel")


def main():
    monitor = Monitor()
    cid = 0
    for i in range(NCARS):
        # if 0 <= i <= 10:
        #     direction = NORTH
        # elif 11 <= i <= 13:
        #     direction = SOUTH
        # elif 13 <= i <= 23:
        #     direction = NORTH
        # elif i > 23:
        #     direction = SOUTH

        direction = NORTH if random.randint(0, 1) == 1 else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1 / 0.5))  # a new car enters each 0.5s

if __name__ == "__main__":
    main()