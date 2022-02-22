# author @mtbvc
# 20/06/2013
# example usage of utils.py functions
#
#
import utils

WIDTH  = 800
HEIGHT = 600
#-----------------

utils.take_screen_shot('http://www.facebook.com/','./','fb.png',800,600)
#utils.crop_screen_shot('fb.png')
utils.halve_screen_shot('fb.png','hfb.png')

#-----------------
#pages = ['http://www.google.com/', 'http://www.facebook.com/', 'http://news.ycombinator.com/']
#files = ['g.png', 'fb.png', 'hn.png']

#for page, filename in zip(pages, files):
#        utils.take_screen_shot(page,'examples/',filename,WIDTH,HEIGHT)
#------------------


