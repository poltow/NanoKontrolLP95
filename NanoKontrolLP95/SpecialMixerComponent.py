# -*- coding: utf-8 -*-
from consts import *
from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller
from _Framework.ChannelStripComponent import * # Class attaching to the mixer of a given track
from _Framework.EncoderElement import EncoderElement
from _Framework.CompoundComponent import CompoundComponent # Base class for classes encompasing other components to form complex components
from _Framework.InputControlElement import * # Base class for all classes representing control elements on a controller
from _Framework.MixerComponent import MixerComponent # Class encompassing several channel strips to form a mixer
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller
from SpecialChannelStripComponent import SpecialChannelStripComponent

class SpecialMixerComponent(MixerComponent):
    ' Special mixer class that uses return tracks alongside midi and audio tracks and allows to navigate sends and reset them'
    __module__ = __name__

    def __init__(self, control_surface, num_tracks, num_returns, EQ, Filter):
        self._tracks_to_use_callback = None
        MixerComponent.__init__(self, num_tracks, num_returns, EQ, Filter)
        # SENDS
        self._sends_index = 0
        self._control_surface = control_surface
        self._button_up = None
        self._button_down = None
        self._send_controls = []
        self._send_reset = []
        self._knobs = []

    def disconnect(self):
        MixerComponent.disconnect(self)
        self._tracks_to_use_callback = None

    def tracks_to_use(self):
        if linked:
            tracks = tuple()
            if self._tracks_to_use_callback != None:
                tracks = self._tracks_to_use_callback()
            else:
                #tracks = MixerComponent.tracks_to_use(self)
                tracks = (self.song().visible_tracks) #+ self.song().return_tracks)
            return tracks
        else:
            return (self.song().visible_tracks) #+ self.song().return_tracks)
        
    def set_tracks_to_use_callback(self, callback):
        self._tracks_to_use_callback = callback
        
    def set_knobs(self, knobs):
        self._knobs = knobs        

    def _create_strip(self):
        return SpecialChannelStripComponent()

    def set_resetsend_buttons(self, buttons):
        # SET BUTTONS FOR RESETTING SEND VALUES AND ADDING LISTENERS
        assert isinstance(buttons, tuple)
        assert (len(buttons) is num_tracks)
        for button in buttons:
            assert isinstance(button, ButtonElement) or (button == None)
        for button in self._send_reset:
            if (button != None):
                button.remove_value_listener(self.reset_send)
        self._send_reset = []
        for button in buttons:
            if (button != None):
                button.add_value_listener(self.reset_send, identify_sender = True)
            self._send_reset.append(button)

    def reset_send(self, value, sender):
        # SET TO 0 THE SEND KNOB WE CONTROL NOW AT A TRACK
        assert (self._send_reset != None)
        assert isinstance(value, int)
        #returns = self.returns_to_use()
        if value is not 0:
            if self.channel_strip(self._send_reset.index(sender))._send_controls[self._sends_index].mapped_parameter() != None:
                if(send_on_off == True):
                    if(self.channel_strip(self._send_reset.index(sender))._send_controls[self._sends_index].mapped_parameter().value==0):
                        self.channel_strip(self._send_reset.index(sender))._send_controls[self._sends_index].mapped_parameter().value = 1.0
                    else:  
                        self.channel_strip(self._send_reset.index(sender))._send_controls[self._sends_index].mapped_parameter().value = 0
                else:
                    self.channel_strip(self._send_reset.index(sender))._send_controls[self._sends_index].mapped_parameter().value = 0
                

    def _set_send_nav(self, send_up, send_down):
        # SET BUTTONS TO NAVIGATE THROUGH TRACKSENDS KNOBS
        if (send_up is not self._button_up):
            # do_update = True
            if (self._button_up != None):
                self._button_up.remove_value_listener(self._send_up_value)
            self._button_up = send_up
            if (self._button_up != None):
                self._button_up.add_value_listener(self._send_up_value)
        if (send_down is not self._button_down):
            if (self._button_down != None):
                self._button_down.remove_value_listener(self._send_down_value)
            self._button_down = send_down
            if (self._button_down != None):
                self._button_down.add_value_listener(self._send_down_value)

    # THE FOLLOWING TWO FUNCTIONS ARE CALLED WHEN THE SEND UP/DOWN BUTTONS ARE CALLED, IT UPDATES TO NEW SEND'S INDEX
    def _send_up_value(self, value):
        assert isinstance(value, int)
        assert isinstance(self._button_up, ButtonElement)
        if value is 127 or not self._button_up.is_momentary():
            if self._sends_index < (len(self.song().return_tracks) - 1):
                self._sends_index = self._sends_index + 1
        self._update_send_index()

    def _send_down_value(self, value):
        assert isinstance(value, int)
        assert isinstance(self._button_down, ButtonElement)
        if value is 127 or not self._button_down.is_momentary():
            if self._sends_index > 0:
                self._sends_index = self._sends_index - 1
        self._update_send_index()

    # UPDATES THE CONTROL SENDS OF A TRACK
    def _update_send_index(self):
        for index in range(8):
            self._send_controls = []
            strip = self.channel_strip(index)
            for i in range(12):
                self._send_controls.append(None)
            self._send_controls[self._sends_index] = self._knobs[index]
            if len(self.song().return_tracks) > 0:
                self._control_surface.show_message("SEND CONTROLLED IS: " + str(self.song().return_tracks[self._sends_index].name))
            strip.set_send_controls(tuple(self._send_controls))
            
        self._button_down.set_light(self._sends_index != 0)
        self._button_up.set_light(self._sends_index != (len(self.song().return_tracks) - 1))

    def _next_track_value(self, value):
        assert (self._next_track_button != None)
        assert (value != None)
        assert (isinstance(value, int))
        if (self.is_enabled() and (value is not 0 or not self._next_track_button.is_momentary())):
            selected_track = self.song().view.selected_track
            all_tracks = tuple(self.song().visible_tracks)
            if selected_track in all_tracks:
                if selected_track != all_tracks[-1]:
                    index = list(all_tracks).index(selected_track)
                    self.song().view.selected_track = all_tracks[index + 1]

    def _prev_track_value(self, value):
        assert (self._next_track_button != None)
        assert (value != None)
        assert (isinstance(value, int))
        if (self.is_enabled() and (value is not 0 or not self._next_track_button.is_momentary())):
            selected_track = self.song().view.selected_track
            all_tracks = tuple(self.song().visible_tracks)
            if selected_track in all_tracks:
                if selected_track != all_tracks[0]:
                    index = list(all_tracks).index(selected_track)
                    self.song().view.selected_track = all_tracks[index - 1]
