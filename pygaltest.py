import pygal
import base64
import struct
import os


d64 = 'vECCQrIOmEI8b6lCf4O5QnPQx0Ls+dNCQ7LdQvF15ELrDOhCSlnoQkRR5UIY699CSSnbQtF510JvGtVCLEvUQvMW1UIrhNZCBXTYQgj32kIuJN5CUxPiQju05kL3FOxCsTvyQvhd+EJjWfxC7tD/QnBuAUPuyAJDFPsDQ/zqBEO5NQVDNXkFQ9a4BUPB9QVDPzEGQ4hsBkP9qAZDAegGQygrB0MFdAdDc8QHQ2weCENGhAhDm/gIQ3F+CUNhGQpDt80KQ6KgC0ORmAxDor0NQ31sDkMfVg5D39kNQ1wyDUMIdgxDhawLQ3PlCkPkMApD46EJQ0mnBkNYFwRDms8BQ9/e/kJttvpCCP/2QrQ180LeV+9CTGXrQmxc50IGPeNCowffQpu92kLGYNZCcPPRQjV4zUKH5chCz6TDQphrvkJfArlCzWizQsDerUIDKKhCKEaiQjo9nEL/D5ZCecGPQhxViUIizoJCF2B4Qvj8akIxel1CVN9PQgE0QkJGgDRCX8wmQn0gGUIghQtC3wX8Qc=='

d = base64.decodestring(d64)

fmt = 'f'
times = len(d) / struct.calcsize(fmt)
fmt_full = '<' + fmt * times
values = struct.unpack(fmt_full, d)

print len(values)
ch = pygal.Line(fill=True, show_dots=False, width=510, height=350, show_legend=False)
ch.add('Torque', values)
filename = os.path.join(os.path.dirname(__file__), 'ch.png')
ch.render_in_browser()
