import pygtk
pygtk.require('2.0')
import gtk
from os import path
import json
import codecs
import sys


class LoginManager:
    def __init__(self):
        f = codecs.open(path.join(path.dirname(__file__), '../accounts'))
        self.accounts = json.load(f)
        f.close()

    def init_gui(self):
        b = gtk.Builder()
        b.add_from_file(path.join(path.dirname(__file__), 'login_dialog.glade'))

        self.dialog = b.get_object('dialog')
        self.treeview_accounts = b.get_object('treeview_accounts')
        liststore_accounts = b.get_object('liststore_accounts')

        self.treeview_accounts.connect('row-activated', lambda *args: self.dialog.response(gtk.RESPONSE_OK))
        self.treeview_accounts.get_selection().connect('changed', self.treeview_accounts_selection_changed)
        self.button_ok = b.get_object('button_ok')
        for acc_id, acc_data in self.accounts.iteritems():
            liststore_accounts.append([acc_data['name'], acc_id])

    def treeview_accounts_selection_changed(self, selection):
        item = selection.get_selected()[1]
        self.button_ok.set_sensitive(bool(item))


    def do_login(self):
        if len(sys.argv) >= 2:
            autoconnect = True
            acc_id = sys.argv[1]
        else:
            autoconnect = False
            self.init_gui()
            response = self.dialog.run()
            if response != gtk.RESPONSE_OK:
                return None
            store, item = self.treeview_accounts.get_selection().get_selected()
            if not item:
                return None
            acc_id = store.get_value(item, 1)
            self.dialog.destroy()
        return self.accounts.get(acc_id), autoconnect
