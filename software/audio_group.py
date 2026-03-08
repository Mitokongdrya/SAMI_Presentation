import os
import random
import queue

class AudioGroup:
    def __init__(self, group_name, audio_folder_path, is_voice=True, voice_type="Matt", audio_file_encoding=".wav"):
        self._group_name = group_name
        self._is_voice = is_voice
        self._voice_type = voice_type
        self._audio_folder_path = audio_folder_path
        self._audio_file_encoding = audio_file_encoding
        self._clip_list = []
        self._clip_queue = queue.SimpleQueue()
        self.rng = random.Random()
        group_dir = os.path.join(self._audio_folder_path, self._group_name)
        # Try and get the group clips froma group folder first
        group_clips = self._get_clips_in_folder(group_dir)
        if group_clips is None:
            # if that doesn't work, let's try by name!
            group_clips = self._get_clips_in_folder(self._audio_folder_path,self._group_name)
            if group_clips is None:
                return False
            else:
                # build the audio list!
                self._clip_list = [os.path.join(self._audio_folder_path, clip) for clip in group_clips]
        else:
            self._audio_folder_path = group_dir
            # build the audio list!
            self._clip_list = [os.path.join(self._audio_folder_path, clip) for clip in group_clips]
        self._update_clip_queue()
        
    @property
    def group_name(self):
        return self._group_name

    def get_clip(self,play_probability=1.0):
        if self.rng.random() < play_probability:
            clip = self._clip_queue.get_nowait()
            self._update_clip_queue()
            return clip
        else:
            print(f"Skipping audio '{clip_name}' due to probability check.")
            return ""

    def _update_clip_queue(self):
        """
        Checks if the queue is empty
        If empty, shuffle our list of call options
        Then stuff them into the queue
        """
        if not self._clip_queue.empty():
            return
        random.shuffle(self._clip_list)
        for clip in self._clip_list:
            self._clip_queue.put_nowait(clip)

    def _get_clips_in_folder(self,check_dir,starts_with=""):
        group_clips = None
        if os.path.isdir(check_dir):
            if self._is_voice:
                group_clips = [
                f for f in os.listdir(check_dir)
                if f.startswith(starts_with) and f.endswith(self._audio_file_encoding) and f"_{self._voice_type}" in f
                ]
            else:
                group_clips = [
                f for f in os.listdir(check_dir)
                if f.startswith(starts_with) and f.endswith(self._audio_file_encoding) in f
                ]
        return group_clips

