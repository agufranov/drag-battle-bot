import threading
import random
from datetime import datetime
import os
import random
import logging
from collections import OrderedDict

from mylib.observable.event import Event
from mylib.observable.dict import ObservableDict
from mylib.observable.property import ObservableProperty
from mylib.worker import Worker

from ll.proxy import Proxy
from .buff import Buff
from .car import Car
from .part import Part, car_part_types
from .task import Task
from .curve import go


class Player:
    def __init__(self, uid, auth):
        self._uid = uid
        self._auth = auth
        self._lock = threading.RLock()

        self.logger = self.get_logger()

        self.is_connected = ObservableProperty(False)

    def get_logger(self):
        logger = logging.getLogger('DragClient')
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('[%(asctime)s] %(message)s', '%d.%m %H:%M:%S')
        console_handler = logging.StreamHandler()
        console_handler.formatter = formatter
        file_handler = logging.FileHandler(os.path.dirname(__file__) + '/../logs/log.txt')
        file_handler.formatter = formatter
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
        return logger

    def sync(func):
        def inner(self, *args, **kwargs):
            with self._lock:
                return func(self, *args, **kwargs)
        return inner

# Main functions
    @sync
    def connect(self):
        self.proxy = Proxy.get_proxy(self._uid, self._auth)
        
        self.garage = {}
        self.workers = []
        self.task_queue = ObservableDict({})

        self.get_driver_info()
        self.get_garage_info()
        self.get_stats(process_events=False)
        self.inv = ObservableDict(self.get_inventory_info())
        self.get_4()
        self.get_daily_bonus_info()
        self.get_news()

        self.update_interval = random.randint(30, 50)
        self.update_worker = Player.update_loop(self)
        self.update_worker.start()
        self.workers.append(self.update_worker)

        self.work_worker = Player.work_loop(self, 3, 1)
        self.work_worker.start()
        self.workers.append(self.work_worker)

        self.casino_worker = Player.casino_loop(self)
        self.casino_worker.start()
        self.workers.append(self.casino_worker)

        self.task_queue_worker = Player.task_queue_loop(self)
        self.task_queue_worker.start()
        self.workers.append(self.task_queue_worker)

        self.is_connected.set_value(True)
        self.logger.debug('Connected')

    @sync
    def disconnect(self):
        [worker.stop() for worker in self.workers]
        self.is_connected.set_value(False)
        self.logger.debug('Disconnected')

    @sync
    def request(self, req, params={}, process_events=True, json_object_pairs_hook=None):

        def do_process_events(response):
            events = response.get('events')
            if events:
                for event in events:
                    if event != 0:
                        if event['type'] == 'updateStats':
                            try:
                                self.exp and self.exp.set_value(int(event['free']))
                                self.money and self.money.set_value(int(event['m']))
                                self.gold and self.gold.set_value(int(event['g']))
                            except AttributeError as e:
                                pass
                        elif event['type'] == 'buff_drv':
                            buff = Buff(int(event['id']), int(event['tpy']), event['par'])
                            self.buffs.add(buff.id, buff)
                        elif event['type'] == 'buff_drv_d':
                            self.buffs.remove(int(event['id']))
                        elif event['type'] == 'buff_auto':
                            car_id = int(event['cid'])
                            if self.garage.has_key(car_id):
                                buff = Buff(int(event['id']), int(event['tpy']), event['par'])
                                self.garage[car_id].buffs.add(buff.id, buff)
                        elif event['type'] == 'buff_auto_d':
                            buff_id = int(event['id'])
                            car_id = int(event['cid'])
                            if self.garage.has_key(car_id):
                                self.garage[car_id].buffs.remove(buff_id)
                                for key, value in self.task_queue.dict.iteritems():
                                    if value.car_id == car_id:
                                        self.task_queue.remove(key)
                                        print 'popped from parts queue'
                                        break
                                    
                        elif event['type'] == 'car_part_rm':
                            car_id = int(event['cid'])
                            part_id = int(event['pid'])
                            if self.garage.has_key(car_id):
                                parts = self.garage[car_id].parts
                                for slot_name, part in parts.dict.iteritems():
                                    if part.id == part_id:
                                        part = parts.remove(slot_name)
                                        break
                                self.inv.add(part.id, part)
                        elif event['type'] == 'ProtectionSystemFail':
                            self.logger.critical('ProtectionSystemFail')
                            self.disconnect()

        response = self.proxy.request(req, params, json_object_pairs_hook=json_object_pairs_hook)
        if process_events:
            do_process_events(response)
        return response


# Requests
    @sync
    def get_driver_info(self):
        response = self.request(1, {'id': self.proxy.uid}, process_events=False)

        # Player buffs
        self.buffs = ObservableDict(Buff.parse_buffs(response))

        # Player stats
        self.exp = ObservableProperty(int(response['ef']))
        self.money = ObservableProperty(int(response['m']))
        self.gold = ObservableProperty(int(response['g']))
        self.exp_initial = self.exp.get_value()
        self.money_initial = self.money.get_value()
        self.gold_initial = self.gold.get_value()
        self.exp_add = ObservableProperty(self.exp.get_value() - self.exp_initial)
        self.money_add = ObservableProperty(self.money.get_value() - self.money_initial)
        self.gold_add = ObservableProperty(self.gold.get_value() - self.gold_initial)
        self.exp.on_changed.add_handler(lambda new_value, old_value: self.exp_add.set_value(new_value - self.exp_initial))
        self.money.on_changed.add_handler(lambda new_value, old_value: self.money_add.set_value(new_value - self.money_initial))
        self.gold.on_changed.add_handler(lambda new_value, old_value: self.gold_add.set_value(new_value - self.gold_initial))

    @sync
    def get_garage_info(self):

        def get_car_info(car_id):
            response = self.request(3, {'id': car_id, 'own': self.proxy.uid}, process_events=False)
            return Car(response)

        response = self.request(2, {'id': 0})
        for car_id in response['cl'].split(','):
            car_id_int = int(car_id)
            if car_id_int != 0:
                self.garage[car_id_int] = get_car_info(car_id_int)

    @sync
    def get_stats(self, process_events=True):
         self.request(10, process_events=process_events)

    @sync
    def get_inventory_info(self):
        response = self.request(5, process_events=False)
        parts_list = response.get('list')
        result = {}
        if parts_list:
            for part_data in parts_list:
                if part_data != 0:
                    result[int(part_data['i'])] = Part(part_data)
        return result

    @sync
    def get_4(self):
        self.request(4)

    @sync
    def get_daily_bonus_info(self):

        def get_daily_bonus():
            self.request(13, process_events=False)

        response = self.request(12, process_events=False)
        if int(response['res']) > 0:
            get_daily_bonus()
            self.logger.debug('Daily bonus got!!!')

    @sync
    def get_news(self):
        self.request(11, process_events=False)

    @sync
    def work(self, work_id, work_length):
        self.request(300, {'wid': work_id, 'ts': work_length})

    @sync
    def open_casino(self):
        response = self.request(326)
        timeout = int(response['ostalos'])
        return timeout

    @sync
    def play_casino(self):
        response = self.request(328)
        self.logger.debug('Casino result: %s %s %s' % (response.get('value1'), response.get('value2'), response.get('value3')))
        timeout = int(response['ostalos'])
        return timeout

    @sync
    def mount_part(self, car_id, part_id):
        if not self.inv.dict.has_key(part_id):
            print 'part not found:', part_id, self.inv.dict
        part = self.inv.dict[part_id]
        car = self.garage[car_id]
        slot_number = car.get_first_free_slot_number(part.type)
        if slot_number == None:
            return None
        response = self.request(7, {'cid': car_id, 'pid': part_id, 'slt': slot_number})
        if response.get('res') == '1':
            slot_name = car.find_slot_by_descr(part.type, slot_number)
            car.parts.add(slot_name, part)
            self.inv.remove(part_id)
            return True
        return False

    @sync
    def unmount_part(self, car_id, slot_name):
        slot_descr = car_part_types[slot_name]
        part_type = slot_descr['type']
        slot_number = slot_descr['slot']
        response = self.request(6, {'cid': car_id, 'type': part_type, 'slt': slot_number})
        if response.get('res') == '1':
            return True
        return False

    @sync
    def add_mount_task(self, car_id, part_id):
        task = Task(type=Task.TYPE_MOUNT, car_id=car_id, car_name=self.garage[int(car_id)].name, part_id=part_id, part_name=self.inv.dict[int(part_id)].name)
        self.task_queue.add(task.id, task)

    @sync
    def add_unmount_task(self, car_id, slot_name):
        task = Task(type=Task.TYPE_UNMOUNT, car_id=car_id, car_name=self.garage[int(car_id)].name, slot_name=slot_name)
        self.task_queue.add(task.id, task)

    @sync
    def get_engine_curves(self, car_id):
        response = self.request(41, {'car': car_id}, json_object_pairs_hook=OrderedDict)

        if response['res'] == '0':
            print 'Car isn`t ready for plotting curves', response
            return False
        else:
            go(response)

        #for curve_code, curve_data in curves.iteritems():
            #chart = pygal.Line(fill=True, show_dots=False)
            #chart.x_labels = map(str, range(min, max, step))
            #curve_name = curve_names.get(curve_code) or '[%s]' % curve_code
            #chart.title = curve_name
            #chart.add(curve_name, curve_data)
            ##chart.render_in_browser()


# Worker loops
    @Worker
    def update_loop(self, finish_event):
        while 1:
            finish_event.wait(self.update_interval)
            if finish_event.is_set():
                self.logger.debug('Update worker: finished')
                break
            self.get_stats()

    @Worker
    def work_loop(self, work_id, work_length, finish_event):
        while 1:
            if finish_event.is_set():
                self.logger.debug('Work worker: finished')
                break
            self._lock.acquire()
            finishes = [buff.finish for buff in self.buffs.dict.itervalues() if buff.tpy == 1000]
            if len(finishes) > 0:
                finish = finishes[0]
                timeout = (finish - datetime.now()).total_seconds()
                if timeout > 0:
                    random_addition = random.randrange(15, 120)
                    self.logger.debug('Work worker: waiting for %d + %d seconds' % (timeout, random_addition))
                    self._lock.release()
                    finish_event.wait(timeout + random_addition)
            else:
                self.logger.debug('Work worker: working')
                self.work(work_id, work_length)
            try:
                self._lock.release()
            except:
                pass

    @Worker
    def casino_loop(self, finish_event):
        while 1:
            with self._lock:
                timeout = self.open_casino() + random.randint(4, 12)
                self.logger.debug('Casino worker: timeout = %d' % timeout)
            finish_event.wait(timeout)
            if finish_event.is_set():
                self.logger.debug('Casino worker: finished')
                break
            with self._lock:
                self.play_casino()

    @Worker
    def task_queue_loop(self, finish_event):
        while 1:
            with self._lock:
                if len(self.task_queue.dict) > 0:
                    key = self.task_queue.dict.keys()[0]
                    task = self.task_queue.dict[key]
                    print task.type, task.car_id, task.part_id, task.slot_name
                    if task.type == Task.TYPE_MOUNT:
                        if self.inv.dict.has_key(task.part_id):
                            result = self.mount_part(task.car_id, task.part_id)
                            print 'result:', result
                            if result:
                                #self.task_queue.remove(key)
                                pass
                    elif task.type == Task.TYPE_UNMOUNT:
                        result = self.unmount_part(task.car_id, task.slot_name)
                        print 'result:', result
                        if result:
                            #self.task_queue.remove(key)
                            pass

            finish_event.wait(random.randint(2, 4))
            if finish_event.is_set():
                self.logger.debug('Task queue worker: finished')
                break
