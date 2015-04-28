import gtk
from ..observable.event import Event
from ..observable.dict import ObservableDict


class ObservableDictView(gtk.IconView):
    def __init__(self, model, icon_selector, name_selector, aux_selector = None):
        self.store = gtk.ListStore(gtk.gdk.Pixbuf, str, str, str)
        gtk.IconView.__init__(self, self.store)
        self.on_item_activated = Event()
        self.connect('item-activated', self.item_activated)
        self.set_pixbuf_column(0)
        self.set_text_column(1)
        self.icon_selector = icon_selector
        self.name_selector = name_selector
        self.aux_selector = aux_selector or (lambda key, item: '')
        self.model = model
        for key, item in self.model.dict.iteritems():
            self._model_on_added(self, key, item)
        self.model.on_added.add_handler(self._model_on_added)
        self.model.on_removed.add_handler(self._model_on_removed)

    def item_activated(self, view, path):
        model = view.get_model()
        item_id = model.get(model.get_iter(path), 2)[0]
        self.on_item_activated.fire(item_id)

    def p(self, *args):
        print args

    def _model_on_added(self, obsdict, key, item):
        self.store.append([self.icon_selector(key, item), self.name_selector(key, item), str(key), self.aux_selector(key, item)])

    def _model_on_removed(self, obsdict, key):
        for item in self.store:
            it = item.iter
            if self.store.get(it, 2)[0] == str(key):
                self.store.remove(it)
                break
