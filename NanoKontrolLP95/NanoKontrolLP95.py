from __future__ import with_statement
import Live
import time # We will be using time functions for time-stamping our log file outputs

from consts import *
from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller
from _Framework.ControlSurface import ControlSurface # Central base class for scripts based on the new Framework
from _Framework.InputControlElement import MIDI_CC_TYPE # Base class for all classes representing control elements on a controller
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller


from SpecialSessionComponent import SpecialSessionComponent
from SpecialMixerComponent import SpecialMixerComponent
from SpecialTransportComponent import SpecialTransportComponent


class NanoKontrolLP95(ControlSurface):
    __module__ = __name__
    __doc__ = " NanoKontrolLP95 controller script "

    def __init__(self, c_instance):
        ControlSurface.__init__(self, c_instance)
        #self._suppress_session_highlight = True
        self._suppress_send_midi = True  # Turn off rebuild MIDI map until after we're done setting up
        Live.Base.log(time.strftime("%d.%m.%Y %H:%M:%S", time.localtime()) + "--------------= NanoKontrolLP95 log opened =--------------") # Writes message into Live's main log file. This is a ControlSurface method.
        with self.component_guard():
            # OBJECTS
            self._session = None #session object
            self._mixer = None #mixer object
            self._transport = None #transport object
            
            # MODES
            self._shift_button = None
            self._cycle_button = None

            # INITIALIZE MIXER, SESSIONS
            self._setup_session_control()  # Setup the session object
            
            self._track_left_button = None
            self._track_right_button = None
            self._setup_mixer_control() # Setup the mixer object
            self._session.set_mixer(self._mixer) # Bind mixer to session

            self._play_button = None
            self._stop_button = None
            self._rec_button = None
            self._setup_transport_control() # Setup transport object
            # SET INITIAL SESSION/MIXER AND MODIFIERS BUTTONS
            
            self.set_highlighting_session_component(self._session)

            for component in self.components:
                component.set_enabled(True)

        self._suppress_send_midi = True # Turn rebuild back on, once we're done setting up
        Live.Base.log("NanoKontrolLP95 Loaded !")


    def _setup_session_control(self):
        # CREATE SESSION, SET OFFSETS, BUTTONS NAVIGATION AND BUTTON MATRIX
        self._session = SpecialSessionComponent(num_tracks, num_scenes) #(num_tracks, num_scenes)
        self._session.set_offsets(0, 0)

    def _setup_mixer_control(self):
        #CREATE MIXER, SET OFFSET (SPECIALMIXERCOMPONENT USES SPECIALCHANNELSTRIP THAT ALLOWS US TO UNFOLD TRACKS WITH TRACK SELECT BUTTON)
        self._mixer = SpecialMixerComponent(num_tracks, 0, False, False) # 8 tracks, 2 returns, no EQ, no filters
        self._mixer.name = 'Mixer'
        self._mixer.set_track_offset(0) #Sets start point for mixer strip (offset from left)
        self._track_left_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, track_left_btn)
        self._track_right_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, track_right_btn)        
        self._mixer.set_select_buttons(self._track_right_button,self._track_left_button)
        self._init_mixer_controls()

    def _setup_transport_control(self):
        # CREATE TRANSPORT DEVICE
        self._transport = SpecialTransportComponent(self)
        self._play_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, play_btn)
        self._stop_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, stop_btn)
        self._rec_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, rec_btn)
        
        self._transport.set_stop_button(self._stop_button)
        self._transport.set_play_button(self._play_button)
        self._transport.set_record_button(self._rec_button)
        
    def connect_script_instances(self, instanciated_scripts):
        #Live.Base.log("connect_script_instances - Start")
        #Live.Base.log("connect_script_instances - self._control_surfaces()=" + str(self._control_surfaces()))
        if(linked):
            for control_surface in self._control_surfaces():
                #Live.Base.log("connect_script_instances - control_surface=" + str(control_surface))
                control_surface_session = control_surface.highlighting_session_component()
                if control_surface_session:
                    if(control_surface_session!=self._session):
                        #Live.Base.log("connect_script_instances - control_surface_session=" + str(control_surface_session))
                        self._session.sync_to(control_surface_session)
                        self._on_track_list_changed()
                        break


    #MODES ARE HERE: INITIALIZATIONS, DISCONNECTS BUTTONS, SLIDERS, ENCODERS
    def _clear_controls(self):
        # TURNING OFF ALL LEDS IN MATRIX
        # SESSION
        
        for index in range(num_tracks):
            strip = self._mixer.channel_strip(index)
            strip.set_solo_button(None)
            strip.set_mute_button(None)
            strip.set_arm_button(None)
            strip.set_pan_control(None)
            strip.set_volume_control(None)
        
        # MIXER
        self._mixer._set_send_nav(None, None)

        # TRANSPORT
        self._transport.set_stop_button(None)
        self._transport.set_play_button(None)
        self._transport.set_record_button(None)

        self._play_button = None
        self._stop_button = None
        self._rec_button = None
        self._track_left_button = None
        self._track_right_button = None

        Live.Base.log("Controls Cleared")

    def _init_mixer_controls(self):
        is_momentary = True
       
        ### SET ARM, SOLO, MUTE
        for index in range(num_tracks):
            strip = self._mixer.channel_strip(index)
            strip.set_solo_button(ButtonElement(is_momentary, MIDI_CC_TYPE, CHANNEL, track_solo_cc[index]))
            strip.set_mute_button(ButtonElement(is_momentary, MIDI_CC_TYPE, CHANNEL, track_mute_cc[index]))
            strip.set_arm_button(ButtonElement(is_momentary, MIDI_CC_TYPE, CHANNEL, track_arm_cc[index]))
            strip.set_pan_control(SliderElement(MIDI_CC_TYPE, CHANNEL, mixer_knob_cc[index]))
            strip.set_volume_control(SliderElement(MIDI_CC_TYPE, CHANNEL, mixer_fader_cc[index]))

    def disconnect(self):
        """clean things up on disconnect"""
        self._clear_controls()
        self._session = None
        self._mixer = None
        self._transport = None

        ControlSurface.disconnect(self)
        return None
