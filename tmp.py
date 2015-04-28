import gtk


w = gtk.Window()
s = gtk.StatusIcon()

def s_a(statusicon):
    if w.get_visible() and not w.is_active():
        w.iconify()
        w.deiconify()
    #w.set_visible(not w.get_visible())
    print w.is_active()

w.connect('delete-event', w.hide_on_delete)
s.set_from_stock(gtk.STOCK_ADD)
s.connect('activate', s_a)
s.connect('popup-menu', gtk.main_quit)

w.show()
gtk.threads_init()
gtk.main()
