from progress.bar import Bar
import time

bar = Bar('Processing', max=100)
for i in range(100):
    time.sleep(0.02)
    bar.next()
bar.finish()

from alive_progress import alive_bar
from time import sleep

with alive_bar(100) as bar:   # default setting
    for i in range(100):
        sleep(0.03)
        bar()                        # call after consuming one item

# using bubble bar and notes spinner
with alive_bar(100, bar = 'bubbles', spinner = 'notes2') as bar: #
    for i in range(100):
        sleep(0.03)
        bar()                        # call after consuming one item