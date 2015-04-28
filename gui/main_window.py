# -*- coding: utf-8 -*-
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import random
from os import path
from datetime import datetime
from mylib.gtk.dictview import ObservableDictView
from gui import icons


class MainWindow:
    def __init__(self, player, name, autoconnect):
        self.player = player
        self.player.is_connected.on_changed.add_handler(self.player_is_connected_changed)

        b = gtk.Builder()
        b.add_from_file(path.join(path.dirname(__file__), 'main_window.glade'))

        self.window = b.get_object('window')
        self.statusicon = b.get_object('statusicon')
        self.toggleaction_connect = b.get_object('toggleaction_connect')
        self.action_exit = b.get_object('action_exit')
        self.garage_container = b.get_object('frame_cars')
        self.inv_container = b.get_object('scrolledwindow_inv')
        self.buffs_container = b.get_object('vbox_buffs')
        self.task_queue_container = b.get_object('alignment_task_queue')
        self.exp_label = b.get_object('label_exp')
        self.money_label = b.get_object('label_money')
        self.gold_label = b.get_object('label_gold')
        self.exp_add_label = b.get_object('label_exp_add')
        self.money_add_label = b.get_object('label_money_add')
        self.gold_add_label = b.get_object('label_gold_add')
        self.action_engine = b.get_object('action_engine')

        self.window.connect('delete-event', self.window.hide_on_delete)
        self.window.connect('key-press-event', self.window_key_press)
        self.statusicon.connect('popup-menu', gtk.main_quit)
        self.statusicon.connect('activate', self.statusicon_activate)
        self.window.set_title(name)
        self.statusicon.set_tooltip_text(name)
        self.statusicon.set_visible(True)
        self.toggleaction_connect.connect('toggled', self.toggleaction_connect_toggled)
        self.action_exit.connect('activate', self.action_exit_activate)
        self.action_engine.connect('activate', self.action_engine_activate)

        if autoconnect:
            self.toggleaction_connect.activate()

    def toggleaction_connect_toggled(self, action):
        if action.get_active():
            self.player.connect()
        else:
            self.player.disconnect()

    def action_engine_activate(self, action):
        self.player.get_engine_curves(self.get_current_car_id())

    def statusicon_activate(self, statusicon):
        self.window.set_visible(not self.window.get_visible())

    def window_key_press(self, window, event):
        key = gtk.gdk.keyval_name(event.keyval)
        if key == 'Escape':
            self.action_exit.activate()
        elif key == 'c':
            self.toggleaction_connect.set_active(not self.toggleaction_connect.get_active())

    def player_is_connected_changed(self, new_value, old_value):
        # If connected
        if new_value:
            self.statusicon.set_from_stock(gtk.STOCK_YES)

            # Player stats
            self.exp_label.set_markup('%d' % self.player.exp.get_value())
            self.money_label.set_markup('%d' % self.player.money.get_value())
            self.gold_label.set_markup('%d' % self.player.gold.get_value())
            self.player.exp.on_changed.add_handler(lambda new_value, old_value: self.exp_label.set_markup('<b>%d</b>' % new_value))
            self.player.money.on_changed.add_handler(lambda new_value, old_value: self.money_label.set_markup('<b>%d</b>' % new_value))
            self.player.gold.on_changed.add_handler(lambda new_value, old_value: self.gold_label.set_markup('<b>%d</b>' % new_value))

            self.exp_add_label.set_markup('+%d' % self.player.exp_add.get_value())
            self.money_add_label.set_markup('+%d' % self.player.money_add.get_value())
            self.gold_add_label.set_markup('+%d' % self.player.gold_add.get_value())
            self.player.exp_add.on_changed.add_handler(lambda new_value, old_value: self.exp_add_label.set_markup('<b>+%d</b>' % new_value))
            self.player.money_add.on_changed.add_handler(lambda new_value, old_value: self.money_add_label.set_markup('<b>+%d</b>' % new_value))
            self.player.gold_add.on_changed.add_handler(lambda new_value, old_value: self.gold_add_label.set_markup('<b>+%d</b>' % new_value))

            gui_buff_containers = []

            # Player buffs
            player_buffs_view = ObservableDictView(self.player.buffs, lambda key, item: icons.buff_icons.get(item.tpy) or icons.buff_icons[-1], lambda key, item: '', lambda key, item: str(item.finish_ts))
            player_buffs_view.set_selection_mode(gtk.SELECTION_NONE)
            player_buffs_view.set_item_width(128)
            player_buffs_view.show()
            gui_buff_containers.append(player_buffs_view)
            for child in self.buffs_container.children():
                self.buffs_container.remove(child)
            self.buffs_container.pack_start(player_buffs_view, False)

            # Player cars
            self.garage_view = gtk.Notebook()
            self.garage_view.show()
            for child in self.garage_container.children():
                self.garage_container.remove(child)
            self.garage_container.add(self.garage_view)
            for car in self.player.garage.itervalues():
                car_label = gtk.Label(car.name)
                car_label.show()

                # Car buffs
                car_buffs_view = ObservableDictView(car.buffs, lambda key, item: icons.buff_icons.get(item.tpy) or icons.buff_icons[-1], lambda key, item: '', lambda key, item: str(item.finish_ts))
                car_buffs_view.set_selection_mode(gtk.SELECTION_NONE)
                car_buffs_view.set_item_width(128)
                car_buffs_view.show()
                gui_buff_containers.append(car_buffs_view)
                self.buffs_container.pack_start(car_buffs_view, False)

                # Car parts
                car_parts_view = ObservableDictView(car.parts, lambda key, item: icons.part_icon, lambda key, item: item.name)
                car_parts_view.on_item_activated.add_handler(self.car_parts_view_item_activated(car.id))
                car_container = gtk.ScrolledWindow()
                car_container.set_data('car_id', car.id)
                car_container.add(car_parts_view)
                car_container.show_all()
                self.garage_view.append_page(car_container, car_label)

            # Player parts
            inv_view = ObservableDictView(self.player.inv, lambda key, item: icons.part_icon, lambda key, item: item.name)
            inv_view.on_item_activated.add_handler(self.inv_view_item_activated)
            inv_view.set_columns(1)
            inv_view.show()
            for child in self.inv_container.children():
                self.inv_container.remove(child)
            self.inv_container.add(inv_view)

            # Player task queue
            task_queue_view = ObservableDictView(self.player.task_queue, lambda key, item: icons.task_queue_icons[item.type], lambda key, item: item.text)
            task_queue_view.show()
            for child in self.task_queue_container.children():
                self.task_queue_container.remove(child)
            self.task_queue_container.add(task_queue_view)

            # Update buff countdowns
            gobject.timeout_add(1000, self.update_buff_countdowns, gui_buff_containers)

        # If disconnected
        else:
            self.statusicon.set_from_stock(gtk.STOCK_NO)

    def action_exit_activate(self, action):
        self.toggleaction_connect.set_active(False)
        gtk.main_quit()

    def show(self):
        self.window.show_all()
        gtk.threads_init()
        gtk.main()

    def update_buff_countdowns(self, gui_buff_containers):
        for container in gui_buff_containers:
            for item in container.get_model():
                finish = datetime.fromtimestamp(int(item[3]))
                if finish > datetime.now():
                    item[1] = self.get_time_repr((finish - datetime.now()).total_seconds())
                else:
                    item[1] = 'Ожидание...'
        return True

    def get_time_repr(self, seconds):
        hrs, hr_secs = divmod(round(seconds), 3600)
        mins, secs = divmod(hr_secs, 60)
        if hrs == 0:
            return '%.2d:%.2d' % (mins, secs)
        else:
            return '%.2d:%.2d:%.2d' % (hrs, mins, secs)

    def inv_view_item_activated(self, part_id):
        #self.player.mount_part(int(car_id), int(part_id))
        self.player.add_mount_task(self.get_current_car_id(), part_id)

    def get_current_car_id(self):
        return self.garage_view.children()[self.garage_view.current_page()].get_data('car_id')

    def car_parts_view_item_activated(self, car_id):
        def handler(slot_name):
            #self.player.unmount_part(int(car_id), slot_name)
            self.player.add_unmount_task(car_id, slot_name)
        return handler
