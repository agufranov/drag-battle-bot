# -*- coding: utf-8 -*-
import random
from .part import car_part_types, part_names


class Task:
    TYPE_MOUNT = 0
    TYPE_UNMOUNT = 1
    def __init__(self, type, car_id, car_name, part_id=None, part_name=None, slot_name=None):
        self.type = type
        self.car_id = int(car_id)
        self.car_name = car_name
        self.part_id = int(part_id) if part_id != None else None
        self.slot_name = slot_name
        self.text = '<Задача>'
        if self.type == Task.TYPE_MOUNT:
            self.text = 'Поставить %s на %s' % (part_name, self.car_name)
        elif self.type == Task.TYPE_UNMOUNT:
            self.text = 'Снять %s с %s' % (part_names[car_part_types[self.slot_name]['type']], self.car_name)
        self.id = random.random()
