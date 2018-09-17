from __future__ import with_statement
import Live
import time # We will be using time functions for time-stamping our log file outputs

from consts import *
from _Framework.ButtonElement import ButtonElement # Class representing a button a the controller
from _Framework.ControlSurface import ControlSurface # Central base class for scripts based on the new Framework
from _Framework.InputControlElement import MIDI_CC_TYPE # Base class for all classes representing control elements on a controller
from _Framework.SliderElement import SliderElement # Class representing a slider on the controller
from _Framework.Profile import profile
from SpecialSessionComponent import SpecialSessionComponent
from SpecialMixerComponent import SpecialMixerComponent
from SpecialTransportComponent import SpecialTransportComponent

LONG_PRESS = 0.5
MON_STATE_NAMES = ['in', 'auto', 'off']
SYNC_TO = {'<Launchpad95'}
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
            self._last_button_time = time.time()
            self._io_list_index = 0
            
            self._setup_controls()

            self._setup_session_control()  # Setup the session object
            self._setup_mixer_control() # Setup the mixer object
            self._session.set_mixer(self._mixer) # Bind mixer to session
            self._setup_transport_control() # Setup transport object

            self._set_mode_button()
            self._set_normal_mode()
            self._track = self.song().view.selected_track
            
            self.set_highlighting_session_component(self._session)

            self._flash_counter = 0
            self._flash_on = True
            
            for component in self.components:
                component.set_enabled(True)

        self._suppress_send_midi = True # Turn rebuild back on, once we're done setting up
        Live.Base.log("NanoKontrolLP95 Loaded !")

    def disconnect(self):
        """clean things up on disconnect"""
        if self._cycle_button != None:
            self._cycle_button.remove_value_listener(self._cycle_button_value)
        self._clear_controls()
        self._transport.set_stop_button(None)
        self._transport.set_play_button(None)
        self._transport.set_rec_button(None)

        self._solo_buttons = None 
        self._mute_buttons = None 
        self._arm_buttons = None 
        self._knobs = None 
        self._faders = None 

        self._ff_button = None
        self._rwd_button = None
        self._play_button = None
        self._stop_button = None
        self._rec_button = None
        
        self._track_left_button = None
        self._track_right_button = None
        self._cycle_button = None
        
        self._set_button = None    
        self._mrk_left_button = None
        self._mrk_right_button = None
        
        self._session = None
        self._mixer = None
        self._transport = None

        ControlSurface.disconnect(self)
    
    def _setup_controls(self):
        self._track_left_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, track_left_btn)
        self._track_right_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, track_right_btn)    
        self._cycle_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, cycle_btn)
        self._cycle_button_active = False             
        
        self._set_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, set_btn)        
        self._mrk_left_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, mrk_left_btn)
        self._mrk_right_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, mrk_right_btn)

        self._ff_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, ff_btn)
        self._rwd_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, rwd_btn)        
        self._play_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, play_btn)
        self._stop_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, stop_btn)
        self._rec_button = ButtonElement(True, MIDI_CC_TYPE, CHANNEL, rec_btn)
        
        self._solo_buttons = [ButtonElement(True, MIDI_CC_TYPE, CHANNEL, track_solo_cc[index]) for index in range(num_tracks)] 
        self._mute_buttons = [ButtonElement(True, MIDI_CC_TYPE, CHANNEL, track_mute_cc[index]) for index in range(num_tracks)] 
        self._arm_buttons = [ButtonElement(True, MIDI_CC_TYPE, CHANNEL, track_arm_cc[index]) for index in range(num_tracks)] 
        self._knobs = [SliderElement(MIDI_CC_TYPE, CHANNEL, mixer_knob_cc[index]) for index in range(num_tracks)] 
        self._faders = [SliderElement(MIDI_CC_TYPE, CHANNEL, mixer_fader_cc[index]) for index in range(num_tracks)] 
    
    
    def _setup_session_control(self):
        # CREATE SESSION, SET OFFSETS, BUTTONS NAVIGATION AND BUTTON MATRIX
        self._session = SpecialSessionComponent(num_tracks, num_scenes) #(num_tracks, num_scenes)
        self._session.set_offsets(0, 0)

    def _setup_mixer_control(self):
        #CREATE MIXER, SET OFFSET (SPECIALMIXERCOMPONENT USES SPECIALCHANNELSTRIP THAT ALLOWS US TO UNFOLD TRACKS WITH TRACK SELECT BUTTON)
        self._mixer = SpecialMixerComponent(self, num_tracks, 0, False, False) # 8 tracks, 2 returns, no EQ, no filters
        self._mixer.name = 'Mixer'
        self._mixer.set_track_offset(0) #Sets start point for mixer strip (offset from left)
        self._mixer.set_select_buttons(self._track_right_button,self._track_left_button)
        self._mixer.set_knobs(self._knobs)
    def _setup_transport_control(self):
        # CREATE TRANSPORT DEVICE
        self._transport = SpecialTransportComponent(self)
        self._transport.set_stop_button(self._stop_button)
        self._transport.set_play_button(self._play_button)
        self._transport.set_rec_button(self._rec_button)
        
    def connect_script_instances(self, instanciated_scripts):
        #Live.Base.log("connect_script_instances - Start")
        #Live.Base.log("connect_script_instances - self._control_surfaces()=" + str(self._control_surfaces()))
        if(linked):
            for control_surface in self._control_surfaces():
                control_surface_type = str(control_surface)
                for sync_master in SYNC_TO:
                    if(control_surface_type.startswith(sync_master)):
                        control_surface_session = control_surface.highlighting_session_component()
                        if control_surface_session:
                            self._session.sync_to(control_surface_session)
                            self._on_track_list_changed()
                            break


    def _clear_controls(self):
            
        if (self._ff_button != None):
            self._ff_button.remove_value_listener(self._out_value)
            self._ff_button.turn_off()
    
        if (self._rwd_button != None):
            self._rwd_button.remove_value_listener(self._in_value)
            self._rwd_button.turn_off()           
            
        if (self._set_button != None):
            self._set_button.remove_value_listener(self._monitor_value)
            self._set_button.remove_value_listener(self._dup_track_value)           
            
        if (self._mrk_left_button != None):
            self._mrk_left_button.remove_value_listener(self._sub_in_value)
            self._mrk_left_button.remove_value_listener(self._new_midi_value)            
            
        if (self._mrk_right_button != None):
            self._mrk_right_button.remove_value_listener(self._sub_out_value)
            self._mrk_right_button.remove_value_listener(self._new_audio_value)            

        # SESSION
        resetsend_controls = []
        self._mixer.send_controls = []
        self._session.set_stop_track_clip_buttons(None)

        # MIXER
        self._mixer._set_send_nav(None, None)
        for track_index in range(num_tracks):
            strip = self._mixer.channel_strip(track_index)
            strip.set_solo_button(None)
            strip.set_mute_button(None)
            strip.set_arm_button(None)
            resetsend_controls.append(None)
            strip.set_select_button(None)
            for i in range(12):
                self._mixer.send_controls.append(None)
            strip.set_send_controls(tuple(self._mixer.send_controls))
        self._mixer.set_resetsend_buttons(tuple(resetsend_controls))
        self.log_message("Controls Cleared")

    def _set_mode_button(self):
        if self._cycle_button != None:
            self._cycle_button.remove_value_listener(self._cycle_button_value)
            self._cycle_button.add_value_listener(self._cycle_button_value)
            self._cycle_button.set_light(self._cycle_button_active)

    def _cycle_button_value(self, value):
        assert (value in range(128))        
        if self._cycle_button != None:
            if value is not 0:
                self._cycle_button_active = not self._cycle_button_active
                self._clear_controls()
                if self._cycle_button_active:
                    self._set_alt_mode()
                else:
                    self._set_normal_mode()
                self.update()   
            
    def _set_normal_mode(self):
        for index in range(num_tracks):
            strip = self._mixer.channel_strip(index)
            strip.set_solo_button(self._solo_buttons[index])
            strip.set_mute_button(self._mute_buttons[index])
            strip.set_arm_button(self._arm_buttons[index])
            strip.set_pan_control(self._knobs[index])
            strip.set_volume_control(self._faders[index])
        self._set_in_out_nav_listeners()    
        self.show_message("IN/OUT SETUP - MUTE SOLO ARM")
                        
    def _set_alt_mode(self):
        self._mixer._set_send_nav(self._ff_button, self._rwd_button)
        stop_track_controls = []
        resetsend_controls = []
        # SET SESSION TRACKSTOP, TRACK SELECT, RESET SEND KNOB
        for index in range(num_tracks):
            strip = self._mixer.channel_strip(index)
            strip.set_select_button(self._solo_buttons[index])
            stop_track_controls.append(self._arm_buttons[index])
            resetsend_controls.append(self._mute_buttons[index])
        self._session.set_stop_track_clip_buttons(tuple(stop_track_controls))
        self._mixer.set_resetsend_buttons(tuple(resetsend_controls))
        self._mixer._update_send_index()
        self._set_create_track_listeners()
        self.show_message("TRACK CREATE DEL DUPE - SEL STOP RESET SEND")
        
    def _set_in_out_nav_listeners(self):
        if (self._ff_button != None):
            self._ff_button.add_value_listener(self._out_value)
    
        if (self._rwd_button != None):
            self._rwd_button.add_value_listener(self._in_value)
            
        if (self._set_button != None):
            self._set_button.add_value_listener(self._monitor_value)
            
        if (self._mrk_left_button != None):
            self._mrk_left_button.add_value_listener(self._sub_in_value)
            
        if (self._mrk_right_button != None):
            self._mrk_right_button.add_value_listener(self._sub_out_value)                                                
        self.update()
           
    def _monitor_value(self, value):
        now = time.time()
        if(value is not 0):
            self._last_button_time = now
        else:
            song = self.song()
            if self._track in song.tracks:
                if now - self._last_button_time < LONG_PRESS:            
                    if not self._track.is_foldable:
                        self._track.current_monitoring_state = (self._track.current_monitoring_state + 1) % 3
                else:  
                    self._set_default_io()            

    def _set_default_io(self):
        if self._track.has_midi_input:
                self._track.input_routing_type = list(self._track.available_input_routing_types)[0]
                if self._track.has_audio_output:
                    if self._track.is_grouped:
                        self._track.output_routing_type = list(self._track.available_output_routing_types)[2]       
                    else:
                        self._track.output_routing_type = list(self._track.available_output_routing_types)[1]
                else:
                    self._track.output_routing_type = list(self._track.available_output_routing_types)[-1]
        else:
                self._track.input_routing_type = list(self._track.available_input_routing_types)[-1]
                if self._track.is_grouped:
                    self._track.output_routing_type = list(self._track.available_output_routing_types)[2]       
                else:
                    self._track.output_routing_type = list(self._track.available_output_routing_types)[1]
                    
        self._track.input_routing_channel = list(self._track.available_input_routing_channels)[0]            
        self._track.output_routing_channel = list(self._track.available_output_routing_channels)[0]  
        self.show_message("TRACK: " + str(self._track.name) + ' INPUT - OUTPUT RESET ')                             
                                     
    def _in_value(self, value):
        if(value is not 0):
            routings = list(self._track.available_input_routing_types)
            current_routing = self._track.input_routing_type
            if current_routing in routings:
                new_index = (routings.index(current_routing) + 1) % len(routings)
                self._track.input_routing_type = routings[new_index]
                route = ' INPUT: ' +  str(self._track.input_routing_type.display_name)
                self.show_message("TRACK: " + str(self._track.name) + route)
            self.update()
            
    def _out_value(self, value):
        if(value is not 0):
            routings = list(self._track.available_output_routing_types)
            current_routing = self._track.output_routing_type
            if current_routing in routings:
                new_index = (routings.index(current_routing) + 1) % len(routings)
                self._track.output_routing_type = routings[new_index]
                route = ' OUTPUT: ' +  str(self._track.output_routing_type.display_name)
                self.show_message("TRACK: " + str(self._track.name) + route)
        self.update()

    def _sub_in_value(self, value):
        if(value is not 0):
            routings = list(self._track.available_input_routing_channels)
            current_routing = self._track.input_routing_channel
            if current_routing in routings:
                new_index = (routings.index(current_routing) + 1) % len(routings)
                self._track.input_routing_channel = routings[new_index]
                route = ' SUB_INPUT: ' +  str(self._track.input_routing_channel.display_name)
                self.show_message("TRACK: " + str(self._track.name) + route)
            self.update()
     
    def _sub_out_value(self, value):
        if(value is not 0):
            routings = list(self._track.available_output_routing_channels)
            current_routing = self._track.output_routing_channel
            if current_routing in routings:
                new_index = (routings.index(current_routing) + 1) % len(routings)
                self._track.output_routing_channel = routings[new_index]
                route = ' SUB_OUTPUT: ' +  str(self._track.output_routing_channel.display_name)
                self.show_message("TRACK: " + str(self._track.name) + route)                       
            self.update()


    def _on_selected_track_changed(self):
        # ALLOWS TO GRAB THE FIRST DEVICE OF A SELECTED TRACK IF THERE'S ANY
        ControlSurface._on_selected_track_changed(self)
        self._track = self.song().view.selected_track
              
    def update(self):
        ControlSurface.update(self)
        self._cycle_button.set_light(self._cycle_button_active)
        
        
    def _set_create_track_listeners(self):
        if (self._set_button != None):
            self._set_button.add_value_listener(self._dup_track_value)
            
        if (self._mrk_left_button != None):
            self._mrk_left_button.add_value_listener(self._new_midi_value)
            
        if (self._mrk_right_button != None):
            self._mrk_right_button.add_value_listener(self._new_audio_value)                                                
        self.update()            
        
    def _dup_track_value(self, value):
        now = time.time()
        if(value is not 0):
            self._last_button_time = now
        else:
            song = self.song()
            if self._track in song.tracks:
                if now - self._last_button_time < LONG_PRESS:            
                    song.duplicate_track(list(song.tracks).index(self._track))
                else:  
                    song.delete_track(list(song.tracks).index(self._track))

    def _new_audio_value(self, value):
        if(value is not 0):
            self._add_track(self.song().create_audio_track)
            
    def _new_midi_value(self, value):
        if(value is not 0):
            self._add_track(self.song().create_midi_track)
            
    def _add_track(self, func):
        song = self.song()
        index = list(song.tracks).index(self._track) + 1
        if index < len(song.tracks) and index >0:
            track = song.tracks[index]
            if track.is_foldable or track.is_grouped:
                while index < len(song.tracks) and song.tracks[index].is_grouped:
                    index += 1
        func(index)
        
    @profile
    def update_display(self):
        super(NanoKontrolLP95, self).update_display()
        self._flash_counter = self._flash_counter + 1
        if self._cycle_button_active  == True:
            if(self._flash_counter % 2  == 0):
                if (self._flash_on == True):
                    self._cycle_button.send_value(127) 
                else:
                    self._cycle_button.send_value(0) 
                self._flash_on = not self._flash_on
                self._flash_counter = self._flash_counter % 4                                                  