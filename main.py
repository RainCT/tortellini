#! /usr/bin/env python
# -.- coding: utf-8 -.-
#
# Copyright © 2012 Siegfried-Angel Gevatter Pujals <siegfried@gevatter.com>
#
# Permission to use, copy, modify, and/or distribute this software for any
# purpose with or without fee is hereby granted, provided that the above
# copyright notice and this permission notice appear in all copies.
#
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR
# ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES
# WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN
# ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF
# OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.

import sys
from gi.repository import Clutter, Cogl, GLib

class State(Clutter.Actor):

    _text = None
    _padding = 10
    _border = 2

    def __init__(self):
        Clutter.Actor.__init__(self)

        self.add_action(Clutter.DragAction())
        self.set_reactive(True)

        self._text = Clutter.Text()
        self._text.set_color(
            Clutter.Color.new(0, 0, 0, 255))
        self._text.set_text("...")
        self._text.set_editable(True)
        self.add_child(self._text)

        self._color = Cogl.Color()
        self._color.init_from_4f(1.0, 1.0, 0.5, 1.0)
        self._border_color = Cogl.Color()
        self._border_color.init_from_4f(0.8, 0.8, 0.5, 1.0)
        self._width = 300
        self._height = 120

    def set_text(self, text):
        self._text.set_text(text)
    
    def do_paint(self):
        allocation = self.get_allocation_box()
        (width, height) = allocation.get_size()

        Cogl.clip_push_rectangle(0, 0, width, height)

        Cogl.set_source_color(self._border_color)
        Cogl.path_rectangle(0, 0, width, height)
        Cogl.path_close()
        Cogl.path_fill()

        Cogl.set_source_color(self._color)
        Cogl.path_rectangle(self._border, self._border,
                            width - self._border, height - self._border)
        Cogl.path_close()
        Cogl.path_fill()

        Cogl.clip_pop()

        Clutter.Actor.do_paint(self)

    def do_pick(self, color):
        if not self.should_pick_paint():
            return

        allocation = self.get_allocation_box()
        (width, height) = allocation.get_size()

        Cogl.clip_push_rectangle(0, 0, width, height)

        cogl_color = Cogl.Color()
        cogl_color.init_from_4ub(color.red, color.green, color.blue, color.alpha)
        Cogl.set_source_color(cogl_color)
        Cogl.path_rectangle(0, 0, width, height)
        Cogl.path_fill()

        Cogl.clip_pop()
        
        for child in self.get_children():
            child.paint()

    def do_allocate(self, allocation, flags):
        Clutter.Actor.do_allocate(self, allocation, flags)

        (width, height) = allocation.get_size()
        availW = width - 2 * self._padding
        availH = width - 2 * self._padding

        child = self._text # self.get_child_at_index(0)
        (minW, minH, natW, natH) = child.get_preferred_size()

        child_box = Clutter.ActorBox()
        child_box.set_size(min(availW, natW), min(availH, natH))
        child_box.set_origin(self._padding, self._padding)
        child.allocate(child_box, flags)

    def do_get_preferred_width(self, for_height):
        minW, natW = Clutter.Actor.do_get_preferred_width(self, for_height)
        extra = 2 * self._padding
        return (minW + extra, natW + extra)

    def do_get_preferred_height(self, for_width):
        minH, natH = Clutter.Actor.do_get_preferred_height(self, for_width)
        extra = 2 * self._padding
        return (minH + extra, natH + extra)
   
    def do_button_press_event(self, event):
        if event.modifier_state & Clutter.ModifierType.CONTROL_MASK:
            return True

    def do_key_focus_in(self):
        pass
        #self._text.grab_key_focus()

    def do_key_focus_out(self):
        print "out"

class MainWindow(Clutter.Stage):

    _selecting_from = None

    def __init__(self):
        Clutter.Stage.__init__(self)
        self.set_size(800, 400)
        self.connect("destroy", lambda x: Clutter.main_quit())
        self.set_title("Tortellini - State Machine editor")
        self.set_color(Clutter.Color.new(255, 255, 255, 255))

        state1 = State()
        state1.set_text("Open Door & Enter Restaurant")
        state1.set_position(10, 10)
        self.add_child(state1)

        state = State()
        state.set_text("Enter_Room")
        state.set_position(10, 50)
        self.add_child(state)

        state = State()
        state.set_text("Intro")
        state.set_position(150, 50)
        self.add_child(state)

        state = State()
        state.set_text("Start_Mapper")
        state.set_position(240, 50)
        self.add_child(state)

        self.show_all()

    def do_button_press_event(self, event):
        clicked = self.get_actor_at_pos(Clutter.PickMode.REACTIVE,
                                         event.x, event.y)
        if event.modifier_state & Clutter.ModifierType.CONTROL_MASK:
            print "(selected)", clicked
            self._selecting_from = clicked
        else:
            if not clicked.has_key_focus():
                clicked.grab_key_focus()
            elif clicked == self:
                self._add_new_object((event.x, event.y))

    def do_button_release_event(self, event):
        released = self.get_actor_at_pos(Clutter.PickMode.REACTIVE,
                                         event.x, event.y)
        if self._selecting_from:
            if isinstance(released, State) and released != self._selecting_from:
                print "yey"
            self._selecting_from = None

    def do_key_release_event(self, event):
        if self.has_key_focus() and event.keyval == Clutter.KEY_space:
            print "Hi, thou have pressed the SPACE key."
    
    def _add_new_object(self, position):
        state = State()
        state.set_position(*position)
        self.add_child(state)
        state.grab_key_focus()

def main():
    GLib.threads_init()
    Clutter.init(sys.argv)

    MainWindow()

    Clutter.main()

def force_exit():
    print 'bye'
    Clutter.main_quit()

if __name__ == '__main__':
    main()
