import Live
import time
from _Framework.ButtonElement import ButtonElement
from _Framework.TransportComponent import TransportComponent

LONG_PRESS = 0.5

class SpecialTransportComponent(TransportComponent):

    def __init__(self, parent):
        TransportComponent.__init__(self)
        self.__mainscript__ = parent
        self._song = self.song()
        self._play_btn = None
        self._last_play_time = time.time()
        self._stop_btn = None
        self._last_stop_time = time.time()
        self._rec_btn = None
        self._last_rec_time = time.time()
        self.song().add_is_playing_listener(self._on_playing_status_changed)
        self.song().add_session_record_listener(self._on_rec_status_changed)

    def disconnect(self):
        self.song().remove_is_playing_listener(self._on_playing_status_changed)
        self.song().remove_session_record_listener(self._on_rec_status_changed)
        self._rec_btn = None
        self._stop_btn = None
        self._play_btn = None
        TransportComponent.disconnect(self)

    def set_stop_button(self, button=None):
        assert isinstance(button, (ButtonElement, type(None)))
        if (self._stop_btn != None):
            self._stop_btn.remove_value_listener(self._stop_btn_value)
        self._stop_btn = button
        if (self._stop_btn != None):
            self._stop_btn.add_value_listener(self._stop_btn_value)
            self._stop_btn.turn_off()

    def set_play_button(self, button):
        assert isinstance(button, (ButtonElement, type(None)))
        if (self._play_btn != None):
            self._play_btn.remove_value_listener(self._play_btn_value)
        self._play_btn = button
        if (self._play_btn != None):
            self._play_btn.add_value_listener(self._play_btn_value)
            self._play_btn.turn_off()
        
    def set_rec_button(self, button):
        assert isinstance(button, (ButtonElement, type(None)))
        if (self._rec_btn != None):
            self._rec_btn.remove_value_listener(self._rec_btn_value)
        self._rec_btn = button
        if (self._rec_btn != None):
            self._rec_btn.add_value_listener(self._rec_btn_value)
            self._rec_btn.turn_off()   
            
            
            
    def _play_btn_value(self, value):
        #Live.Base.log("SpecialProSessionComponent _undo_button_value: " + str(value) + " - enabled:" + str(self.is_enabled()))
        assert (value in range(128))        
        if self.is_enabled() and self._play_btn != None:
            now = time.time()
            if value is not 0:
                self._last_play_time = now
            else:
                if now - self._last_play_time < LONG_PRESS:
                    self._song.is_playing = not self._song.is_playing
                else:
                    self.song().view.follow_song = not self.song().view.follow_song
            self.update()
            
    def _on_playing_status_changed(self):
        if self.is_enabled():
            if self._play_btn:
                
                self._play_btn.set_light(self._song.is_playing)


    def _rec_btn_value(self, value):
        #Live.Base.log("SpecialProSessionComponent _undo_button_value: " + str(value) + " - enabled:" + str(self.is_enabled()))
        assert (value in range(128))        
        if self.is_enabled() and self._rec_btn != None:
            now = time.time()
            if value is not 0:
                self._last_rec_time = now
            else:
                if now - self._last_rec_time < LONG_PRESS:
                    self._song.session_record = not self._song.session_record
                else:
                    self._song.record_mode = not self._song.record_mode
            self.update()  
            
            
    def _on_rec_status_changed(self):
        if self.is_enabled():
            if self._rec_btn:
                self._rec_btn.set_light(self._song.session_record)   
                
                
    def _stop_btn_value(self, value):
        #Live.Base.log("SpecialProSessionComponent _undo_button_value: " + str(value) + " - enabled:" + str(self.is_enabled()))
        assert (value in range(128))        
        if self.is_enabled() and self._stop_btn != None:
            now = time.time()
            if value is not 0:
                self._last_stop_time = now
                self._stop_btn.turn_on()
            else:
                self._stop_btn.turn_off()
                if now - self._last_stop_time < LONG_PRESS:
                    self._song.stop_playing()
                else:
                    self._song.stop_all_clips()
            self.update()