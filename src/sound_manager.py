import pygame as pg
import os
import random

class SoundManager:
    """Handles all game sounds and music"""
    def __init__(self, game):
        self.game = game
        self.sounds = {}
        self.music = None
        self.volume = 0.7  # Default volume
        self.music_volume = 0.4  # Default music volume
        self.enabled = True
        self.music_enabled = True
        
        # Load sounds
        self.load_sounds()
        
    def load_sounds(self):
        """Load all game sound effects"""
        # Create the sounds directory if it doesn't exist
        sound_dir = os.path.join("assets", "sounds")
        os.makedirs(sound_dir, exist_ok=True)
        
        # Define sound effects to load
        sound_files = {
            "jump": ["jump.wav", "jump2.wav"],
            "land": ["land.wav"],
            "token_collect": ["collect.wav", "collect2.wav"],
            "door_open": ["door_open.wav"],
            "death": ["death.wav"],
            "level_complete": ["level_complete.wav"],
            "menu_click": ["click.wav"],
            "menu_hover": ["hover.wav"]
        }
        
        # Load each sound if file exists
        for sound_name, filenames in sound_files.items():
            self.sounds[sound_name] = []
            for filename in filenames:
                file_path = os.path.join(sound_dir, filename)
                if os.path.exists(file_path):
                    sound = pg.mixer.Sound(file_path)
                    self.sounds[sound_name].append(sound)
                else:
                    # Create placeholder sounds with appropriate durations and frequencies
                    self._create_placeholder_sound(sound_name, filename)
        
        # Set volumes
        self.set_volumes()
        
    def _create_placeholder_sound(self, sound_name, filename):
        """Create placeholder sounds until real sound assets are added"""
        # Create a sound buffer based on the sound type
        sound_dir = os.path.join("assets", "sounds")
        file_path = os.path.join(sound_dir, filename)
        
        # Generate different placeholder sounds based on type
        sample_rate = 44100  # Standard sample rate
        bit_depth = -16      # 16-bit
        
        if "jump" in sound_name:
            # Create a short ascending tone for jumping
            duration = 0.2  # 200ms
            frequency = 800  # Higher pitch
            sound_array = self._generate_sine_wave(duration, frequency, sample_rate, ascending=True)
            
        elif "land" in sound_name:
            # Create a short descending thud for landing
            duration = 0.15
            frequency = 300  # Lower pitch
            sound_array = self._generate_sine_wave(duration, frequency, sample_rate, ascending=False)
            
        elif "collect" in sound_name:
            # Create a short high-pitched ping for token collection
            duration = 0.15
            frequency = 1200
            sound_array = self._generate_sine_wave(duration, frequency, sample_rate)
            
        elif "door" in sound_name:
            # Create a sliding sound for door
            duration = 0.4
            frequency = 400
            sound_array = self._generate_sine_wave(duration, frequency, sample_rate, sliding=True)
            
        elif "death" in sound_name:
            # Create a dramatic sound for death
            duration = 0.5
            frequency = 200
            sound_array = self._generate_noise(duration, sample_rate)
            
        elif "complete" in sound_name:
            # Create a triumphant sound for level completion
            duration = 1.0
            sound_array = self._generate_arpeggio(duration, sample_rate)
            
        elif "click" in sound_name:
            # Create a click sound
            duration = 0.05
            frequency = 800
            sound_array = self._generate_click(duration, sample_rate)
            
        elif "hover" in sound_name:
            # Create a subtle hover sound
            duration = 0.05
            frequency = 600
            sound_array = self._generate_sine_wave(duration, frequency, sample_rate)
            
        else:
            # Default placeholder sound
            duration = 0.2
            frequency = 500
            sound_array = self._generate_sine_wave(duration, frequency, sample_rate)
        
        # Create sound from array and save to file
        sound = pg.sndarray.make_sound(sound_array)
        
        # Save the sound file for future use
        if not os.path.exists(os.path.dirname(file_path)):
            os.makedirs(os.path.dirname(file_path))
        
        # Add to sounds dictionary
        self.sounds.setdefault(sound_name, []).append(sound)
        
    def _generate_sine_wave(self, duration, frequency, sample_rate, ascending=False, sliding=False):
        """Generate a sine wave sound effect"""
        import numpy as np
        
        num_samples = int(duration * sample_rate)
        buf = np.zeros((num_samples, 2), dtype=np.int16)
        
        # Create amplitude envelope (attack/decay)
        amplitude = np.ones(num_samples)
        attack_samples = min(int(0.1 * sample_rate), num_samples // 2)  # 100ms attack, but not more than half the sample
        decay_samples = min(int(0.1 * sample_rate), num_samples // 2)   # 100ms decay, but not more than half the sample
        
        # Attack phase (ramp up)
        if attack_samples > 0:
            amplitude[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay phase (ramp down)
        if decay_samples > 0 and num_samples > decay_samples:
            amplitude[-decay_samples:] = np.linspace(1, 0, decay_samples)
        
        # Generate sine wave
        t = np.linspace(0, duration, num_samples)
        
        if ascending:
            # Create ascending pitch
            freq_start = frequency * 0.7
            freq_end = frequency * 1.3
            phase = 2 * np.pi * np.linspace(freq_start, freq_end, num_samples) * t
            wave = np.sin(phase)
        elif sliding:
            # Create sliding effect
            phase = 2 * np.pi * frequency * t
            slide = np.sin(2 * np.pi * 3 * t)  # Modulation frequency
            wave = np.sin(phase + 50 * slide)
        else:
            # Standard sine wave
            phase = 2 * np.pi * frequency * t
            wave = np.sin(phase)
        
        # Apply amplitude envelope
        wave = wave * amplitude
        
        # Scale to int16 range and copy to both channels
        wave = wave * 32767 * 0.7  # Reduce volume slightly
        buf[:, 0] = wave.astype(np.int16)
        buf[:, 1] = wave.astype(np.int16)
        
        return buf
        
    def _generate_noise(self, duration, sample_rate):
        """Generate a noise sound effect for dramatic moments"""
        import numpy as np
        
        num_samples = int(duration * sample_rate)
        buf = np.zeros((num_samples, 2), dtype=np.int16)
        
        # Generate white noise
        noise = np.random.uniform(-1, 1, num_samples)
        
        # Apply low-pass filter (simple moving average)
        window_size = 20
        filtered_noise = np.zeros_like(noise)
        for i in range(num_samples):
            start = max(0, i - window_size // 2)
            end = min(num_samples, i + window_size // 2)
            filtered_noise[i] = np.mean(noise[start:end])
        
        # Create amplitude envelope (attack/decay/sustain/release)
        amplitude = np.ones(num_samples)
        attack_samples = int(0.05 * sample_rate)  # 50ms attack
        decay_samples = int(0.1 * sample_rate)    # 100ms decay
        sustain_level = 0.7
        release_samples = int(0.3 * sample_rate)  # 300ms release
        
        # Attack phase
        amplitude[:attack_samples] = np.linspace(0, 1, attack_samples)
        
        # Decay phase
        decay_end = attack_samples + decay_samples
        if decay_end < num_samples:
            amplitude[attack_samples:decay_end] = np.linspace(1, sustain_level, decay_samples)
        
        # Release phase
        release_start = num_samples - release_samples
        if release_start >= 0 and release_start < num_samples:
            amplitude[release_start:] = np.linspace(sustain_level, 0, release_samples)
        
        # Apply amplitude envelope
        filtered_noise = filtered_noise * amplitude
        
        # Scale to int16 range and copy to both channels
        filtered_noise = filtered_noise * 32767 * 0.8
        buf[:, 0] = filtered_noise.astype(np.int16)
        buf[:, 1] = filtered_noise.astype(np.int16)
        
        return buf
    
    def _generate_arpeggio(self, duration, sample_rate):
        """Generate an arpeggio chord for level completion"""
        import numpy as np
        
        # Define notes (basic major chord arpeggio)
        base_freq = 440  # A4
        notes = [
            base_freq,              # Root
            base_freq * 5/4,        # Major 3rd
            base_freq * 3/2,        # Perfect 5th
            base_freq * 2,          # Octave
            base_freq * 2 * 5/4,    # Octave + 3rd
            base_freq * 2 * 3/2     # Octave + 5th
        ]
        
        num_samples = int(duration * sample_rate)
        buf = np.zeros((num_samples, 2), dtype=np.int16)
        
        # Duration of each note
        note_duration = duration / len(notes)
        samples_per_note = int(note_duration * sample_rate)
        
        # Create amplitude envelope for each note
        envelope = np.ones(samples_per_note)
        attack = int(0.1 * samples_per_note)
        decay = int(0.3 * samples_per_note)
        envelope[:attack] = np.linspace(0, 1, attack)
        envelope[-decay:] = np.linspace(1, 0.3, decay)
        
        # Generate each note
        for i, note in enumerate(notes):
            start_sample = i * samples_per_note
            end_sample = min((i + 1) * samples_per_note, num_samples)
            if start_sample >= num_samples:
                break
                
            # Generate note samples
            t = np.linspace(0, note_duration, end_sample - start_sample)
            wave = np.sin(2 * np.pi * note * t)
            
            # Apply envelope
            note_envelope = envelope[:end_sample - start_sample]
            wave = wave * note_envelope
            
            # Add to buffer
            wave = wave * 32767 * 0.7
            buf[start_sample:end_sample, 0] += wave.astype(np.int16)
            buf[start_sample:end_sample, 1] += wave.astype(np.int16)
        
        return buf
    
    def _generate_click(self, duration, sample_rate):
        """Generate a short click sound"""
        import numpy as np
        
        num_samples = int(duration * sample_rate)
        buf = np.zeros((num_samples, 2), dtype=np.int16)
        
        # Just a sharp pulse followed by quick decay
        pulse_samples = int(0.01 * sample_rate)  # 10ms pulse
        
        if pulse_samples > 0 and pulse_samples < num_samples:
            # Create pulse
            buf[:pulse_samples, 0] = 32767
            buf[:pulse_samples, 1] = 32767
            
            # Create decay
            decay = np.linspace(32767, 0, num_samples - pulse_samples)
            buf[pulse_samples:, 0] = decay
            buf[pulse_samples:, 1] = decay
        
        return buf
    
    def set_volumes(self):
        """Set volume levels for all sounds"""
        for sound_list in self.sounds.values():
            for sound in sound_list:
                sound.set_volume(self.volume)
    
    def play(self, sound_name):
        """Play a sound effect by name"""
        if not self.enabled or sound_name not in self.sounds or not self.sounds[sound_name]:
            return
            
        # Get a random sound from the list for variety
        sound = random.choice(self.sounds[sound_name])
        sound.play()
        
    def play_jump(self):
        """Play jump sound"""
        self.play("jump")
        
    def play_land(self):
        """Play landing sound"""
        self.play("land")
        
    def play_token_collect(self):
        """Play token collection sound"""
        self.play("token_collect")
        
    def play_door_open(self):
        """Play door open sound"""
        self.play("door_open")
        
    def play_death(self):
        """Play death sound"""
        self.play("death")
        
    def play_level_complete(self):
        """Play level completion sound"""
        self.play("level_complete")
        
    def play_menu_click(self):
        """Play menu click sound"""
        self.play("menu_click")
        
    def play_menu_hover(self):
        """Play menu hover sound"""
        self.play("menu_hover")
        
    def toggle_sound(self):
        """Toggle all sound effects on/off"""
        self.enabled = not self.enabled
        return self.enabled
        
    def set_volume(self, volume):
        """Set volume for all sound effects (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        self.set_volumes()
        
    def play_music(self, music_file=None):
        """Play background music"""
        if not self.music_enabled:
            return
            
        # If no music file specified, check for default music
        if music_file is None:
            music_dir = os.path.join("assets", "sounds")
            music_file = os.path.join(music_dir, "music.mp3")
            
        if os.path.exists(music_file):
            try:
                pg.mixer.music.load(music_file)
                pg.mixer.music.set_volume(self.music_volume)
                pg.mixer.music.play(-1)  # Loop indefinitely
            except:
                print(f"Could not play music: {music_file}")
        
    def stop_music(self):
        """Stop the current background music"""
        pg.mixer.music.stop()
        
    def toggle_music(self):
        """Toggle background music on/off"""
        self.music_enabled = not self.music_enabled
        
        if self.music_enabled:
            self.play_music()
        else:
            self.stop_music()
            
        return self.music_enabled
