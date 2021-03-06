#Embedded file name: /Users/versonator/Jenkins/live/output/mac_64_static/Release/python-bundle/MIDI Remote Scripts/Launchpad/SpecialSessionComponent.py
from _Framework.SessionComponent import SessionComponent
from _Framework.SceneComponent import SceneComponent
import Live

class SpecialSessionComponent(SessionComponent):
    """ Special session subclass that handles ConfigurableButtons """
            
    def __init__(self, num_tracks, num_scenes):
        self._visible_width = num_tracks
        self._visible_height = num_scenes
        self._synced_session = None
        SessionComponent.__init__(self, num_tracks, num_scenes)

    def disconnect(self):
        SessionComponent.disconnect(self)
        if self._synced_session != None:
            self._synced_session.remove_offset_listener(self._on_control_surface_offset_changed)
            self._mixer.set_tracks_to_use_callback(None)


    def set_size(self, width, height):
        assert(width in range(self._num_tracks + 1))
        assert(height in range(len(self._scenes) + 1))
        self._visible_width = width
        self._visible_height = height
        self._show_highlight = False
        self.set_show_highlight(True)

    def width(self):
        return self._visible_width

    def height(self):
        return self._visible_height

    def sync_to(self, other_session):
        assert (isinstance(other_session, (type(None), SessionComponent)))
        if other_session != self._synced_session:
            if self._synced_session != None:
                self._synced_session.remove_offset_listener(self._on_control_surface_offset_changed)
                self._mixer.set_tracks_to_use_callback(None)
            self._synced_session = other_session
            if(self._synced_session != None):
                self._synced_session.add_offset_listener(self._on_control_surface_offset_changed)
            self._mixer.set_tracks_to_use_callback(self._synced_session.tracks_to_use)
        self._do_show_highlight()

    def set_offsets(self, track_offset, scene_offset):
        if self._synced_session != None:
            self._synced_session.set_offsets(track_offset, scene_offset)
        else:
            SessionComponent.set_offsets(self, track_offset, scene_offset)

    def _on_control_surface_offset_changed(self):
        SessionComponent.set_offsets(self, self._synced_session.track_offset(), self._synced_session.scene_offset())

    def _create_scene(self):
        return SceneComponent(self._num_tracks, self.tracks_to_use)

    def _reassign_scenes(self):
        SessionComponent._reassign_scenes(self)
        self.on_selected_scene_changed()
