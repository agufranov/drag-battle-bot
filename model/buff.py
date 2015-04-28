import base64
import struct
from datetime import datetime
import threading


class Buff:
    def __init__(self, id, tpy, par):
        self.id = int(id)
        self.tpy = int(tpy)
        self.finish_ts, = struct.unpack('<Ixxxxxx', base64.decodestring(par))
        self.finish = datetime.fromtimestamp(self.finish_ts)

    def __str__(self):
        return 'Buff [id = %d, tpy = %d, finish = %s]' % (self.id, self.tpy, self.finish)

    @staticmethod
    def parse_buffs(data):
        buffs_data = data.get('_buffs')
        result = {}
        if buffs_data:
            for buff_data in buffs_data:
                if buff_data != 0:
                    buff = Buff(int(buff_data['id']), int(buff_data['tpy']), buff_data['par'])
                    result[buff.id] = buff
        return result
