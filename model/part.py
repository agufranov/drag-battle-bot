# -*- coding: utf-8 -*-
class Part:
    def __init__(self, data):
        try:
            self.type = int(data['t'])
            self.ci = int(data['ci'])
            self.id = int(data['i'])
            self.mod = int(data['mod'])
            self.u = data.has_key('u') and int(data['u']) or None
            self.par = data['par']
            self.name = '%s %d' % (part_names.get(self.type) or '<деталь>', self.ci)
        except Exception as e:
            print data

part_names = {
    2: 'Колесо',
    5: 'Передний бампер',
    12: 'Фильтр',
    13: 'Дроссель',
    14: 'Ресивер',
    15: 'Двигатель',
    16: 'Выпуск. колл.',
    17: 'Маховик',
    18: 'Турбина',
    21: 'КПП',
    22: 'Дифференциал',
    24: 'Трасса',
}

car_part_types = {
    'bwh': { 'type': 2, 'slot': 0 },
    'fwh': { 'type': 2, 'slot': 1 },
    'fb': { 'type': 5, 'slot': 0 },
    '_f': { 'type': 12, 'slot': 0 },
    '_th': { 'type': 13, 'slot': 0 },
    '_rcv': { 'type': 14, 'slot': 0 },
    '_e': { 'type': 15, 'slot': 0 },
    '_exc': { 'type': 16, 'slot': 0 },
    '_c1': { 'type': 18, 'slot': 0 },
    '_c2': { 'type': 18, 'slot': 1 },
    '_gb': { 'type': 21, 'slot': 0 },
    '_dif': { 'type': 22, 'slot': 0 },
    '_ext': { 'type': 24, 'slot': 0 }
}
