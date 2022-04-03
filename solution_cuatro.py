"""
    @author: Óscar Mesa Martín

    4ª solución
"""

from multiprocessing import Process, Lock, Condition, Value
from time import sleep
from random import random
from random import choice

NCARS = 70
NORTH = 1
SOUTH = -1


def delay(factor=3):
    sleep(random()*factor)


class Tunnel(object):
    def __init__(self, capacity=3, ticks_allowed=11, balance=10, nl=True):
        self.lock = Lock()

        self.actualDirection = Value('i', 0)

        self.northSemaphore = Condition(self.lock)
        self.southSemaphore = Condition(self.lock)

        self.northWaiting = Value('i', 0)
        self.southWaiting = Value('i', 0)

        self.northTraffic = Value('i', 0)
        self.southTraffic = Value('i', 0)

        self.ticks = Value('i', 0)
        self.capacity = capacity
        self.ticks_allowed = ticks_allowed
        self.balance = balance

        if nl == False:
            self.end = "\r"
        else:
            self.end = "\n"

    def getTraffic(self):
        return self.northTraffic.value + self.southTraffic.value

    def getTrafficDirection(self):
        return self.actualDirection.value

    def canEnterNorth(self):
        return self.actualDirection.value == NORTH and self.capacity > self.getTraffic()

    def canEnterSouth(self):
        return self.actualDirection.value == SOUTH and self.capacity > self.getTraffic()

    def hasWaitingNorth(self):
        return self.northWaiting.value > 0

    def hasWaitingSouth(self):
        return self.southWaiting.value > 0

    def strEcho(self):
        D_ = ""

        if self.actualDirection.value == NORTH:
            D_ = "N"
        elif self.actualDirection.value == SOUTH:
            D_ = "S"
        else:
            D_ = "-"

        return f" WN {self.northWaiting.value} |" \
               f" WS {self.southWaiting.value} |" \
               f" TN {self.northTraffic.value} |" \
               f" TS {self.southTraffic.value} | {D_}"

    def waits(self, i, direction):
        self.lock.acquire()

        if direction == NORTH:
            self.northWaiting.value += 1
        else:
            self.southWaiting.value += 1

        if self.actualDirection.value == 0 and self.getTraffic() == 0:
            self.actualDirection.value = direction

        print(f"{self.strEcho()} | Car {i} is waiting -> DIR {direction}", end=self.end)
        self.lock.release()

    def isBalanced(self):
        result = True
        if self.getTrafficDirection() == NORTH:
            result = self.southWaiting.value- self.northWaiting.value < self.balance
        elif self.getTrafficDirection() == SOUTH:
            result = self.northWaiting.value- self.southWaiting.value < self.balance
        return result

    def enters(self, i, direction):
        delay()
        self.lock.acquire()

        if direction == NORTH:
            self.northSemaphore.wait_for(self.canEnterNorth)
            self.northWaiting.value -= 1
            self.northTraffic.value += 1
        else:
            self.southSemaphore.wait_for(self.canEnterSouth)
            self.southWaiting.value -= 1
            self.southTraffic.value += 1

        self.ticks.value += 1

        print(f"{self.strEcho()} | Car {i} enters -> DIR {direction}", end=self.end)

        if self.ticks.value >= self.ticks_allowed and\
                self.hasWaitingNorth() and\
                self.hasWaitingSouth() and\
                not self.isBalanced():
            self.ticks.value = 0
            self.actualDirection.value = 0
            print(f"{self.strEcho()} | Semaphore is blocking both directions", end=self.end)

        if self.getTrafficDirection() == NORTH:
            self.northSemaphore.notify()
        elif self.getTrafficDirection() == SOUTH:
            self.southSemaphore.notify()

        self.lock.release()

    def leaves(self, i, direction):
        delay()

        self.lock.acquire()

        if direction == NORTH:
            self.northTraffic.value -= 1
        else:
            self.southTraffic.value -= 1

        print(f"{self.strEcho()} | Car {i} leaves -> DIR {direction}", end=self.end)

        if self.getTraffic() == 0:
            if direction == NORTH:
                if self.southWaiting.value > 0:
                    self.actualDirection.value = SOUTH
                    print(f"{self.strEcho()} | Semaphore changes", end=self.end)
            else:
                if self.northWaiting.value > 0:
                    self.actualDirection.value = NORTH
                    print(f"{self.strEcho()} | Semaphore changes", end=self.end)

        if self.getTrafficDirection() == NORTH:
            self.northSemaphore.notify()
        elif self.getTrafficDirection() == SOUTH:
            self.southSemaphore.notify()

        self.lock.release()


def car_task(tunnel, i, direction):
    tunnel.waits(i, direction)
    tunnel.enters(i, direction)
    tunnel.leaves(i, direction)


def solution_cuatro(nl=True, init_car_factor_delay=0.5):
    cars = []

    tunnel = Tunnel(nl=nl)

    for i in range(NCARS):
        direction = choice([NORTH, SOUTH])
        car = Process(target=car_task, args=(tunnel, i, direction))
        cars.append(car)

    for p in cars:
        p.start()
        delay(init_car_factor_delay)

    for p in cars:
        p.join()

    print("END")


if __name__ == '__main__':
    solution_cuatro(nl=False)