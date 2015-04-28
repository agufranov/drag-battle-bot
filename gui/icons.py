import gtk


theme = gtk.icon_theme_get_default()

part_icon = theme.load_icon(gtk.STOCK_PREFERENCES, 16, 0)
mount_icon = theme.load_icon(gtk.STOCK_GOTO_TOP, 16, 0)
unmount_icon = theme.load_icon(gtk.STOCK_COPY, 16, 0)

buff_icons = {
    1000: theme.load_icon(gtk.STOCK_HOME, 16, 0),
    2000: unmount_icon,
    2001: mount_icon,
    10: theme.load_icon(gtk.STOCK_ADD, 16, 0),
    -1: theme.load_icon(gtk.STOCK_DELETE, 16, 0)
}

task_queue_icons = {
    0: mount_icon,
    1: unmount_icon
}
