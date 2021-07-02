# Plugin to control the Pibooth using Pimoroni Flotilla tools

import pibooth
from pibooth.utils import LOGGER
import flotilla
import pygame
import time

# setup for virtual GPIO event
BUTTON_DOWN = pygame.USEREVENT + 1

__version__ = "0.0.2"

@pibooth.hookimpl
def pibooth_startup(app):
    # setup of the flotilla dock
    app.flotilla_dock = flotilla.Client()
    while not app.flotilla_dock.ready:
        pass

    # set up the items from the dock
    app.flotilla_touch = app.flotilla_dock.first(flotilla.Touch)
    app.flotilla_matrix_1 = app.flotilla_dock.first(flotilla.Matrix)
    app.flotilla_matrix_2 = app.flotilla_dock.second(flotilla.Matrix)
    app.flotilla_number = app.flotilla_dock.first(flotilla.Number)

    # set appropriate matrix rotation TODO: could be config
    app.flotilla_matrix_1.rotation(270)
    app.flotilla_matrix_2.rotation(270)

    # set appropriate number brightness - TODO: could be config
    app.flotilla_number.set_brightness(128)

    LOGGER.info("Flotilla Dock enumeration: '%s' plugin", __name__)
    for module in app.flotilla_dock.available.items():
        LOGGER.info("Module: {} active".format(module))

@pibooth.hookimpl
def state_wait_enter(app):
    # set matrix brightness for message level - lower than flash level TODO: could be config 
    app.flotilla_matrix_1.set_brightness(10)
    app.flotilla_matrix_2.set_brightness(10)

    # this doesn't seem to work? TODO: could be config
    app.flotilla_matrix_1.rotation(r=180)
    app.flotilla_matrix_2.rotation(r=180)


@pibooth.hookimpl
def state_wait_do(cfg, app):
    # setup the display of an icon on the matrix while waiting for a photo print event
    display_icon_smiley = [
        [0, 0, 1, 1, 1, 1, 0, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [1, 0, 0, 0, 1, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 1],
        [1, 0, 1, 1, 0, 1, 0, 1],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [0, 0, 1, 1, 1, 1, 0, 0],
    ]

    display_icon_heart = [
        [0, 1, 1, 1, 0, 0, 0, 0],
        [1, 0, 0, 0, 1, 0, 0, 0],
        [1, 0, 0, 0, 0, 1, 0, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [0, 1, 0, 0, 0, 0, 1, 0],
        [1, 0, 0, 0, 0, 1, 0, 0],
        [1, 0, 0, 0, 1, 0, 0, 0],
        [0, 1, 1, 1, 0, 0, 0, 0],
    ]

    # app.flotilla_matrix_1.set_icon('smiley').update()
    app.flotilla_matrix_1.set_matrix(display_icon_smiley).update()
    app.flotilla_matrix_2.set_matrix(display_icon_heart).update()

    # create a simulated keypress event and add it to the queue on toucj press - allowing the standard processing to continue
    if app.flotilla_touch.one:
        # virtual_touch_event = pygame.event.Event(BUTTON_DOWN, capture=1, printer=0, button=app.buttons.capture)
        LOGGER.debug("Virtual BUTTONDOWN: generate CAPTURE event")
        virtual_touch_event = pygame.event.Event(pygame.locals.KEYDOWN, unicode="p", key=pygame.locals.K_p, mod=pygame.locals.KMOD_NONE)
        pygame.event.post(virtual_touch_event)
        time.sleep(0.3) # hacky debounce

    if app.flotilla_touch.four:
        virtual_touch_event = pygame.event.Event(BUTTON_DOWN, printer=1, capture=0, button=app.buttons.printer)
        LOGGER.debug("Virtual BUTTONDOWN: generate PRINTER event")
        pygame.event.post(virtual_touch_event)
        time.sleep(0.3) # hacky

@pibooth.hookimpl
def state_wait_exit(app):
    # turn off the matrices when leaving the wait state
    app.flotilla_matrix_1.clear().update()
    app.flotilla_matrix_2.clear().update()

    # clearing number from display
    app.flotilla_number.set_string("")
    app.flotilla_number.update()

@pibooth.hookimpl
def state_choose_do(app):
    # use the touch control to pick the capture_nbr variable - fingers crossed this is all that's required
    if app.flotilla_touch.one:
        app.capture_nbr = 1
    if app.flotilla_touch.two:
        app.capture_nbr = 2
    if app.flotilla_touch.three:
        app.capture_nbr = 3
    if app.flotilla_touch.four:
        app.capture_nbr = 4

@pibooth.hookimpl
def state_capture_enter(app):
    # set matrix brightness for flash level - maximum brightness
    app.flotilla_matrix_1.set_brightness(255)
    app.flotilla_matrix_2.set_brightness(255)
    app.flotilla_matrix_1.full().update()
    app.flotilla_matrix_2.full().update()

@pibooth.hookimpl
def state_capture_exit(app):
    app.flotilla_matrix_1.clear().update()
    app.flotilla_matrix_2.clear().update()

@pibooth.hookimpl
def state_processing_enter(app):
    LOGGER.info("Displaying image number: {}".format(app.count.taken))
    app.flotilla_number.set_number(int(app.count.taken))
    app.flotilla_number.update()

    #hack up the app.capture_choices to trick the processing in state_processing_do in picture_plugin.py  into working
    app.capture_choices = (4, app.capture_nbr)

@pibooth.hookimpl
def state_print_do(app):
    # create a simulated keypress event and add it to the queue on toucj press - allowing the standard processing to continue
    if app.flotilla_touch.one:
        virtual_touch_event = pygame.event.Event(BUTTON_DOWN, capture=1, printer=0, button=app.buttons.capture)
        LOGGER.debug("Virtual BUTTONDOWN: generate CAPTURE event")
        # virtual_touch_event_picture = pygame.event.Event(pygame.locals.KEYDOWN, unicode="p", key=pygame.locals.K_p, mod=pygame.locals.KMOD_NONE)
        pygame.event.post(virtual_touch_event)
        # time.sleep(0.3)

    if app.flotilla_touch.four:
        virtual_touch_event = pygame.event.Event(BUTTON_DOWN, printer=1, capture=0, button=app.buttons.printer)
        LOGGER.debug("Virtual BUTTONDOWN: generate PRINTER event")
        pygame.event.post(virtual_touch_event)


@pibooth.hookimpl
def pibooth_cleanup(app):
    LOGGER.info("Stopping Flotilla Dock")
    app.flotilla_dock.stop()
