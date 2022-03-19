"""
Solution to the one-way tunnel
"""
import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value

SOUTH = "south"
NORTH = "north"

NCARS = 10


class Monitor():
    def __init__(self):
        self.mutex = Lock()
        self.south = Value('i', 0)  # number of cars in south direction
        self.north = Value('i', 0)  # number of cars in north direction
        self.no_south = Condition(self.mutex)
        self.no_north = Condition(self.mutex)

    def wants_enter(self, direction):
        self.mutex.acquire()

        if direction == NORTH:
            self.no_south.wait_for(lambda: self.south.value==0)
            self.north.value += 1
        else:
            self.no_north.wait_for(lambda: self.north.value==0)
            self.south.value += 1

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

    # numdir = monitor.north if direction == NORTH else monitor.south
    # print('NUMEROS COCHES EN DIRECCION ' + direction + ' --> ' + numdir)

    print(f"car {cid} heading {direction} leaving the tunnel")
    monitor.leaves_tunnel(direction)
    print(f"car {cid} heading {direction} out of the tunnel")


def main():
    monitor = Monitor()
    cid = 0
    for _ in range(NCARS):
        direction = NORTH if random.randint(0, 1) == 1 else SOUTH
        cid += 1
        p = Process(target=car, args=(cid, direction, monitor))
        p.start()
        time.sleep(random.expovariate(1 / 0.5))  # a new car enters each 0.5s

if __name__ == "__main__":
    main()