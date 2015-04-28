# -*- coding: utf-8 -*-
import threading
from .buff import Buff
from .part import Part, car_part_types
from mylib.observable.event import Event
from mylib.observable.dict import ObservableDict


class Car:
    def __init__(self, data):
        self._lock = threading.RLock()
        self.id = int(data['id'])
        self.par = data['par']
        self.name = car_names.get(self.par) or 'Машина <%s>' % self.par

        # Car buffs
        self.buffs = ObservableDict(Buff.parse_buffs(data))

        # Car parts
        initial_parts = {}
        for slot_name, slot_descr in car_part_types.iteritems():
            part_type = slot_descr['type']
            part_info = data.get(slot_name)
            if part_info:
                part_info['t'] = part_type
                initial_parts[slot_name] = (Part(part_info))
        self.parts = ObservableDict(initial_parts)

    def find_slot_by_descr(self, part_type, slot_number):
        for slot_name, slot_descr in car_part_types.iteritems():
            if slot_descr['type'] == part_type and slot_descr['slot'] == slot_number:
                return slot_name
        return None

    def get_first_free_slot_number(self, part_type):
        slot_number = 0
        while 1:
            slot_name = self.find_slot_by_descr(part_type, slot_number)
            if slot_name != None:
                if not self.parts.dict.has_key(slot_name):
                    return slot_number
                slot_number += 1
            else:
                return None

    def __str__(self):
        return 'Car [id = %d, par = %s]' % (self.id, self.par)


car_names = {
    '/82LAgAAAEwBBgAAAAE=': 'ВАЗ-2101',
    'kgAAAQAAAEwAAAAAAAF=': 'ВАЗ-2108'
}
