import numpy as np
import os
from pydub import AudioSegment
from pedalboard.io import AudioFile
from pedalboard import *
import noisereduce as nr
import io
import wave
import numpy as np
from scipy.signal import butter, filtfilt, sosfilt
import librosa

class DeEsser:
    """
    A custom de-essing processor that reduces harsh sibilance in vocal recordings.
    Handles both mono and stereo audio automatically.
    """
    def __init__(self, threshold=-20, ratio=2, attack_ms=1, release_ms=10):
        self.threshold = threshold
        self.ratio = ratio
        self.attack_ms = attack_ms
        self.release_ms = release_ms
    
    def _create_band_filters(self, sample_rate):
        """Create filters for splitting the signal into frequency bands"""
        nyquist = sample_rate / 2
        low_cutoff = 4000 / nyquist
        high_cutoff = 9000 / nyquist
        
        # Create bandpass filter coefficients in SOS format
        sos = butter(4, [low_cutoff, high_cutoff], btype='band', output='sos')
        return sos
    
    def _compute_envelope(self, audio, sample_rate):
        """
        Calculate the amplitude envelope of the sibilance band.
        Handles both mono and stereo audio.
        
        Parameters:
        audio: numpy array of shape (samples,) for mono or (samples, channels) for stereo
        sample_rate: sampling rate in Hz
        
        Returns:
        envelope: numpy array of the same shape as input
        """
        # Convert attack and release times to samples
        attack_samples = max(1, int(self.attack_ms * sample_rate / 1000))
        release_samples = max(1, int(self.release_ms * sample_rate / 1000))
        
        # Handle both mono and stereo audio
        if audio.ndim == 1:
            # Mono audio processing
            return self._compute_single_channel_envelope(
                audio, attack_samples, release_samples)
        else:
            # Stereo audio processing - process each channel separately
            envelopes = np.zeros_like(audio)
            for channel in range(audio.shape[1]):
                envelopes[:, channel] = self._compute_single_channel_envelope(
                    audio[:, channel], attack_samples, release_samples)
            return envelopes
    
    def _compute_single_channel_envelope(self, audio, attack_samples, release_samples):
        """
        Compute envelope for a single channel of audio.
        
        Parameters:
        audio: 1D numpy array representing a single channel
        attack_samples: attack time in samples
        release_samples: release time in samples
        
        Returns:
        envelope: 1D numpy array of the same length as input
        """
        # Full-wave rectification
        abs_signal = np.abs(audio)
        
        # Initialize envelope
        envelope = np.zeros_like(abs_signal)
        envelope[0] = abs_signal[0]
        
        # Compute envelope sample by sample
        for i in range(1, len(abs_signal)):
            if abs_signal[i] > envelope[i-1]:
                # Attack phase
                envelope[i] = abs_signal[i]
            else:
                # Release phase
                release_factor = 1 - 1/release_samples
                envelope[i] = max(abs_signal[i], envelope[i-1] * release_factor)
        
        return envelope
    
    def _safe_filter(self, audio, sos):
        """
        Safely apply filtering to both mono and stereo audio.
        
        Parameters:
        audio: numpy array of shape (samples,) for mono or (samples, channels) for stereo
        sos: Second-order sections filter coefficients
        
        Returns:
        filtered: filtered audio of the same shape as input
        """
        if audio.ndim == 1:
            # Mono audio
            return sosfilt(sos, audio)
        else:
            # Stereo audio - process each channel separately
            filtered = np.zeros_like(audio)
            for channel in range(audio.shape[1]):
                filtered[:, channel] = sosfilt(sos, audio[:, channel])
            return filtered
    
    def process(self, audio, sample_rate):
        """
        Apply de-essing to the audio signal.
        Handles both mono and stereo audio automatically.
        """
        # Create the filters
        sos = self._create_band_filters(sample_rate)
        
        # Extract sibilance band
        sibilance_band = self._safe_filter(audio, sos)
        
        # Compute the envelope
        envelope = self._compute_envelope(sibilance_band, sample_rate)
        
        # Convert threshold to linear
        threshold_linear = 10 ** (self.threshold / 20)
        
        # Compute gain reduction
        gain_reduction = np.ones_like(envelope)
        mask = envelope > threshold_linear
        gain_reduction[mask] = threshold_linear + (envelope[mask] - threshold_linear) / self.ratio
        gain_reduction[mask] /= envelope[mask]
        
        # Apply gain reduction to sibilance band
        processed_sibilance = sibilance_band * gain_reduction
        
        # Process other frequencies
        sos_low = butter(4, 4000 / (sample_rate/2), btype='low', output='sos')
        other_frequencies = self._safe_filter(audio, sos_low)
        
        return other_frequencies + processed_sibilance


class Equalizer:

    def __init__(self) -> None:
        pass

    def board(self, audio, sample_rate):
        board = Pedalboard([
            PitchShift(semitones=0.2),  # Very subtle pitch shift for slight variation 
            Compressor(threshold_db=-24, ratio=3, attack_ms=20, release_ms=150),  # Softer compression
            HighpassFilter(cutoff_frequency_hz=150),  # Slightly higher cutoff to reduce low-end noise
            LowpassFilter(cutoff_frequency_hz=7000),  # Softer high-end filtering for warmth
            Gain(gain_db=1),  # Minimal gain boost
            NoiseGate(threshold_db=-50),  # Subtle noise gating
            Limiter(threshold_db=-5),  # Final limiter for balances
        ])

        return board(audio, sample_rate)
    
    def to_audiosegment(self, audio, sample_rate):
        if audio.ndim == 1:
            audio = audio.reshape(1, -1)
        elif audio.ndim == 2 and audio.shape[0] > audio.shape[1]:
            audio = audio.T

        audio = np.clip(audio, -1, 1)
        
        processed_int16 = (audio.T * 32767).astype(np.int16)
        
        # Create a bytes buffer to hold the WAV file data
        buffer = io.BytesIO()
        
        # Write the WAV file to the buffer
        with wave.open(buffer, 'wb') as wavfile:
            wavfile.setnchannels(audio.shape[0])  # Number of channels
            wavfile.setsampwidth(2)  # 2 bytes per sample (16-bit)
            wavfile.setframerate(sample_rate)
            wavfile.writeframes(processed_int16.tobytes())
        
        # Reset buffer position to start
        buffer.seek(0)
        audio_segment = AudioSegment.from_wav(buffer)
        return audio_segment
    
    def _audiosegment_to_numpy(self, audio_segment):
        # Get the raw audio data as an array of samples
        samples = np.array(audio_segment.get_array_of_samples())
        
        # Convert to float32 and normalize to [-1.0, 1.0]
        # pydub stores audio as 16-bit integers
        samples = samples.astype(np.float32) / 32767.0
        
        # Handle stereo/mono channel configuration
        if audio_segment.channels == 2:
            # Reshape stereo audio to (samples, 2)
            samples = samples.reshape(-1, 2)
        
        return samples, audio_segment.frame_rate

    def equalize(self, audio_input):

        if isinstance(audio_input, str):
            # Input is a file path
            audio, sample_rate = librosa.load(audio_input, sr=None)
        elif isinstance(audio_input, AudioSegment):
            # Input is an AudioSegment
            audio, sample_rate = self._audiosegment_to_numpy(audio_input)
        else:
            raise ValueError("Input must be either a file path (str) or an AudioSegment object")

        # audio, sample_rate = librosa.load(file_path, sr=None)
        audio = audio / np.max(np.abs(audio))

        deesser = DeEsser(
            threshold=-30,    # Threshold for sibilance detection
            ratio=4,         # Compression ratio for sibilance reduction
            attack_ms=0.5,     # Fast attack to catch transients
            release_ms=15    # Quick release to maintain naturalness
        )

        deessed_audio = deesser.process(audio, sample_rate)
        equalized_audio = self.board(deessed_audio, sample_rate)

        equalized_audio_segment = self.to_audiosegment(equalized_audio, sample_rate)

        return equalized_audio_segment