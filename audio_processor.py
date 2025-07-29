import librosa
import librosa.display
import numpy as np
import scipy.signal
import soundfile as sf
import os
import argparse
import threading
import queue
import time

try:
    import pyaudio
except ImportError:
    print("PyAudio not installed. Real-time processing will be disabled.")
    pyaudio = None

try:
    import speech_recognition as sr
except ImportError:
    print("SpeechRecognition not installed. Speech recognition will be disabled.")
    sr = None

try:
    import tkinter as tk
    from tkinter import ttk
    from tkinter import filedialog
    GUI_ENABLED = True
except ImportError:
    print("Tkinter not installed. GUI will be disabled.")
    GUI_ENABLED = False

# Audio Processing Functions

def noise_reduction_spectral_subtraction(audio, noise_clip, sr, prop_decrease=1.0):
    """Noise reduction using spectral subtraction."""
    noise_stft = librosa.stft(noise_clip)
    noise_stft_db = librosa.amplitude_to_db(np.abs(noise_stft), ref=np.max)
    mean_noise_db = np.mean(noise_stft_db, axis=1)
    noise_stft_smoothed = librosa.db_to_amplitude(mean_noise_db)

    audio_stft = librosa.stft(audio)
    audio_stft_db = librosa.amplitude_to_db(np.abs(audio_stft), ref=np.max)

    reduced_stft_db = np.zeros_like(audio_stft_db)
    for i in range(audio_stft_db.shape[1]):
        reduced_stft_db[:, i] = np.maximum(audio_stft_db[:, i] - prop_decrease * mean_noise_db, -80)  # -80 dB floor

    reduced_stft = librosa.db_to_amplitude(reduced_stft_db)
    reduced_audio = librosa.istft(reduced_stft)

    return reduced_audio

def noise_reduction_wiener(audio, noise_clip, sr, lFilterLength=800):
    """Noise reduction using Wiener filtering."""
    win = int(lFilterLength/2)
    if len(noise_clip) < win:
        return audio
    noise_psd = np.abs(librosa.stft(noise_clip, n_fft=lFilterLength, hop_length=win)).mean(axis=1)
    audio_psd = np.abs(librosa.stft(audio, n_fft=lFilterLength, hop_length=win)).mean(axis=1)
    
    wiener_filter = audio_psd / (audio_psd + noise_psd)

    audio_stft = librosa.stft(audio, n_fft=lFilterLength, hop_length=win)
    filtered_stft = audio_stft * wiener_filter[:, None]
    filtered_audio = librosa.istft(filtered_stft)
    return filtered_audio

def convert_audio_format(input_file, output_file, target_format):
    """Converts audio format using soundfile."""
    try:
        data, samplerate = sf.read(input_file)
        sf.write(output_file, data, samplerate, format=target_format)
        return True
    except Exception as e:
        print(f"Error during format conversion: {e}")
        return False

def extract_features(audio, sr, feature_type='mfcc', n_mfcc=13):
    """Extracts audio features."""
    if feature_type == 'mfcc':
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=n_mfcc)
        return mfccs
    elif feature_type == 'chroma':
        chroma = librosa.feature.chroma_stft(y=audio, sr=sr)
        return chroma
    elif feature_type == 'spectral_centroid':
        spectral_centroid = librosa.feature.spectral_centroid(y=audio, sr=sr)[0]
        return spectral_centroid
    else:
        raise ValueError("Invalid feature type.")

def generate_spectrogram(audio, sr, output_file=None):
    """Generates and saves a spectrogram."""
    X = librosa.stft(audio)
    Xdb = librosa.amplitude_to_db(abs(X))
    
    import matplotlib.pyplot as plt
    plt.figure(figsize=(12, 4))
    librosa.display.specshow(Xdb, sr=sr, x_axis='time', y_axis='hz')
    plt.colorbar()
    plt.title('Spectrogram')
    if output_file:
        plt.savefig(output_file)
    else:
        plt.show()
    plt.close()

def speech_to_text(audio_file):
    """Converts speech to text using SpeechRecognition (Sphinx)."""
    if sr is None:
        print("SpeechRecognition library is not installed.")
        return None

    r = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = r.record(source)

    try:
        text = r.recognize_sphinx(audio)  # Use Sphinx
        return text
    except sr.UnknownValueError:
        return "Sphinx could not understand audio"
    except sr.RequestError as e:
        return f"Sphinx error; {e}"

def generate_sine_wave(frequency, duration, sr=44100):
    """Generates a sine wave."""
    t = np.linspace(0, duration, int(sr * duration), False)
    note = np.sin(2 * np.pi * frequency * t)
    return note

def add_reverb(audio, sr, reverb_time=0.5, decay_rate=0.5):
  """Adds reverb to an audio signal."""
  impulse_response = np.zeros(int(sr * reverb_time))
  impulse_response[0] = 1.0
  for i in range(1, len(impulse_response)):
    impulse_response[i] = impulse_response[i-1] * decay_rate

  reverbed_audio = scipy.signal.convolve(audio, impulse_response, mode='full')[:len(audio)]
  return reverbed_audio

def add_echo(audio, sr, delay=0.2, decay=0.6):
    """Adds echo to an audio signal."""
    delay_samples = int(delay * sr)
    echo = np.zeros_like(audio)
    echo[delay_samples:] = audio[:-delay_samples] * decay
    return audio + echo

def add_distortion(audio, drive=5.0):
  """Adds distortion to an audio signal."""
  distorted_audio = np.tanh(audio * drive)
  return distorted_audio

# Real-Time Audio Processing (PyAudio)

class RealTimeProcessor:
    def __init__(self, chunk=1024, format=pyaudio.paFloat32, channels=1, rate=44100):
        self.chunk = chunk
        self.format = format
        self.channels = channels
        self.rate = rate
        self.p = None
        self.stream = None
        self.running = False
        self.queue = queue.Queue()
        self.effect = None  # Store the chosen effect
        self.effect_params = {} # Store effect parameters

    def set_effect(self, effect_name, effect_params):
         self.effect = effect_name
         self.effect_params = effect_params

    def start(self):
        if pyaudio is None:
            print("PyAudio is not available. Real-time processing cannot start.")
            return
        
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.format,
                                channels=self.channels,
                                rate=self.rate,
                                input=True,
                                output=True,
                                stream_callback=self.callback)
        self.running = True
        threading.Thread(target=self.process_audio, daemon=True).start()

    def stop(self):
        if self.stream:
            self.running = False
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()

    def callback(self, in_data, frame_count, time_info, status):
        try:
            data = np.frombuffer(in_data, dtype=np.float32)
            self.queue.put(data)
            return (in_data, pyaudio.paContinue)  # Pass-through initially
        except Exception as e:
            print(f"Callback error: {e}")
            return (None, pyaudio.paAbort)

    def process_audio(self):
        while self.running:
            try:
                data = self.queue.get(timeout=0.1) # Non-blocking get with timeout

                if self.effect == 'reverb':
                    processed_data = add_reverb(data, self.rate, reverb_time=self.effect_params.get('reverb_time', 0.5), decay_rate=self.effect_params.get('decay_rate', 0.5))
                elif self.effect == 'echo':
                    processed_data = add_echo(data, self.rate, delay=self.effect_params.get('delay', 0.2), decay=self.effect_params.get('decay', 0.6))
                elif self.effect == 'distortion':
                     processed_data = add_distortion(data, drive=self.effect_params.get('drive', 5.0))
                else:
                    processed_data = data # No effect

                # Ensure output data is within the valid range [-1, 1]
                processed_data = np.clip(processed_data, -1, 1).astype(np.float32)

                # Stream the processed audio back
                self.stream.write(processed_data.tobytes())

            except queue.Empty:
                pass # No data available yet

            except Exception as e:
                print(f"Processing error: {e}")
                break

# GUI (Tkinter)

if GUI_ENABLED:
    class AudioProcessorGUI:
        def __init__(self, master):
            self.master = master
            master.title("Advanced Audio Processor")

            self.input_file = tk.StringVar()
            self.output_file = tk.StringVar()
            self.noise_file = tk.StringVar()
            self.selected_effect = tk.StringVar(value="None")
            self.realtime_processor = RealTimeProcessor()

            # Input File Selection
            ttk.Label(master, text="Input File:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(master, textvariable=self.input_file, width=50).grid(row=0, column=1, padx=5, pady=5)
            ttk.Button(master, text="Browse", command=self.browse_input_file).grid(row=0, column=2, padx=5, pady=5)

            # Output File Selection
            ttk.Label(master, text="Output File:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(master, textvariable=self.output_file, width=50).grid(row=1, column=1, padx=5, pady=5)
            ttk.Button(master, text="Browse", command=self.browse_output_file).grid(row=1, column=2, padx=5, pady=5)

            # Noise File Selection (for noise reduction)
            ttk.Label(master, text="Noise File:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
            ttk.Entry(master, textvariable=self.noise_file, width=50).grid(row=2, column=1, padx=5, pady=5)
            ttk.Button(master, text="Browse", command=self.browse_noise_file).grid(row=2, column=2, padx=5, pady=5)

            # Audio Processing Buttons
            ttk.Button(master, text="Noise Reduction (Spectral)", command=self.process_noise_reduction_spectral).grid(row=3, column=0, columnspan=3, pady=5)
            ttk.Button(master, text="Noise Reduction (Wiener)", command=self.process_noise_reduction_wiener).grid(row=4, column=0, columnspan=3, pady=5)
            ttk.Button(master, text="Convert to WAV", command=self.convert_to_wav).grid(row=5, column=0, columnspan=3, pady=5)
            ttk.Button(master, text="Extract MFCC Features", command=self.extract_mfcc).grid(row=6, column=0, columnspan=3, pady=5)
            ttk.Button(master, text="Generate Spectrogram", command=self.generate_spectrogram_gui).grid(row=7, column=0, columnspan=3, pady=5)
            ttk.Button(master, text="Speech to Text", command=self.speech_to_text_gui).grid(row=8, column=0, columnspan=3, pady=5)

            # Audio Synthesis
            ttk.Button(master, text="Generate Sine Wave", command=self.generate_sine_wave_gui).grid(row=9, column=0, columnspan=3, pady=5)

            # Real-time Audio Processing
            ttk.Label(master, text="Real-Time Audio Effects:").grid(row=10, column=0, sticky=tk.W, padx=5, pady=5)
            effects = ["None", "Reverb", "Echo", "Distortion"]
            self.effect_dropdown = ttk.Combobox(master, textvariable=self.selected_effect, values=effects)
            self.effect_dropdown.grid(row=10, column=1, padx=5, pady=5)
            self.effect_dropdown.bind("<<ComboboxSelected>>", self.update_effect_params)

            self.reverb_time_label = ttk.Label(master, text="Reverb Time:")
            self.reverb_time_entry = ttk.Entry(master, width=10)
            self.decay_rate_label = ttk.Label(master, text="Decay Rate:")
            self.decay_rate_entry = ttk.Entry(master, width=10)
            self.delay_label = ttk.Label(master, text="Delay:")
            self.delay_entry = ttk.Entry(master, width=10)
            self.decay_label = ttk.Label(master, text="Decay:")
            self.decay_entry = ttk.Entry(master, width=10)
            self.drive_label = ttk.Label(master, text="Drive:")
            self.drive_entry = ttk.Entry(master, width=10)

            ttk.Button(master, text="Start Real-time Processing", command=self.start_realtime).grid(row=11, column=0, columnspan=3, pady=5)
            ttk.Button(master, text="Stop Real-time Processing", command=self.stop_realtime).grid(row=12, column=0, columnspan=3, pady=5)

        def browse_input_file(self):
            filename = filedialog.askopenfilename()
            self.input_file.set(filename)

        def browse_output_file(self):
            filename = filedialog.asksaveasfilename(defaultextension=".wav")
            self.output_file.set(filename)

        def browse_noise_file(self):
            filename = filedialog.askopenfilename()
            self.noise_file.set(filename)

        def process_noise_reduction_spectral(self):
            input_file = self.input_file.get()
            noise_file = self.noise_file.get()
            output_file = self.output_file.get()
            if not (input_file and noise_file and output_file):
                print("Please select input, noise, and output files.")
                return

            try:
                audio, sr = librosa.load(input_file)
                noise, _ = librosa.load(noise_file, sr=sr)
                reduced_audio = noise_reduction_spectral_subtraction(audio, noise, sr)
                sf.write(output_file, reduced_audio, sr)
                print("Spectral Subtraction Noise Reduction Complete.")
            except Exception as e:
                print(f"Error during spectral subtraction: {e}")

        def process_noise_reduction_wiener(self):
            input_file = self.input_file.get()
            noise_file = self.noise_file.get()
            output_file = self.output_file.get()
            if not (input_file and noise_file and output_file):
                print("Please select input, noise, and output files.")
                return

            try:
                audio, sr = librosa.load(input_file)
                noise, _ = librosa.load(noise_file, sr=sr)
                reduced_audio = noise_reduction_wiener(audio, noise, sr)
                sf.write(output_file, reduced_audio, sr)
                print("Wiener Filter Noise Reduction Complete.")
            except Exception as e:
                print(f"Error during Wiener filtering: {e}")

        def convert_to_wav(self):
            input_file = self.input_file.get()
            output_file = self.output_file.get()
            if not (input_file and output_file):
                print("Please select input and output files.")
                return

            if convert_audio_format(input_file, output_file, 'WAV'):
                print("Audio format conversion to WAV complete.")
            else:
                print("Audio format conversion failed.")

        def extract_mfcc(self):
            input_file = self.input_file.get()
            if not input_file:
                print("Please select an input file.")
                return

            try:
                audio, sr = librosa.load(input_file)
                mfccs = extract_features(audio, sr, feature_type='mfcc')
                print("MFCC Feature Extraction Complete.")
                print("MFCC shape:", mfccs.shape)
            except Exception as e:
                print(f"Error during MFCC extraction: {e}")

        def generate_spectrogram_gui(self):
            input_file = self.input_file.get()
            output_file = self.output_file.get()
            if not (input_file and output_file):
                print("Please select input and output files.")
                return

            try:
                audio, sr = librosa.load(input_file)
                generate_spectrogram(audio, sr, output_file)
                print("Spectrogram generation complete.")
            except Exception as e:
                print(f"Error during spectrogram generation: {e}")

        def speech_to_text_gui(self):
            input_file = self.input_file.get()
            if not input_file:
                print("Please select an input file.")
                return

            text = speech_to_text(input_file)
            if text:
                print("Speech to Text Output:", text)
            else:
                print("Speech to Text Failed.")

        def generate_sine_wave_gui(self):
            output_file = self.output_file.get()
            if not output_file:
                print("Please select an output file.")
                return

            try:
                frequency = 440  # A4 note
                duration = 5      # seconds
                sr = 44100

                sine_wave = generate_sine_wave(frequency, duration, sr)
                sf.write(output_file, sine_wave, sr)
                print("Sine wave generation complete.")
            except Exception as e:
                print(f"Error during sine wave generation: {e}")

        def start_realtime(self):
            selected_effect = self.selected_effect.get()
            effect_params = self.get_effect_params() # Retrieve effect parameters

            self.realtime_processor.set_effect(selected_effect.lower(), effect_params)
            self.realtime_processor.start()
            print("Real-time processing started.")

        def stop_realtime(self):
            self.realtime_processor.stop()
            print("Real-time processing stopped.")

        def update_effect_params(self, event=None):
            selected_effect = self.selected_effect.get()

            # Hide existing parameter widgets
            self.hide_effect_params()

            # Show parameter widgets for the selected effect
            if selected_effect == "Reverb":
                self.reverb_time_label.grid(row=13, column=0, sticky=tk.W, padx=5, pady=5)
                self.reverb_time_entry.grid(row=13, column=1, padx=5, pady=5)
                self.decay_rate_label.grid(row=14, column=0, sticky=tk.W, padx=5, pady=5)
                self.decay_rate_entry.grid(row=14, column=1, padx=5, pady=5)
            elif selected_effect == "Echo":
                self.delay_label.grid(row=13, column=0, sticky=tk.W, padx=5, pady=5)
                self.delay_entry.grid(row=13, column=1, padx=5, pady=5)
                self.decay_label.grid(row=14, column=0, sticky=tk.W, padx=5, pady=5)
                self.decay_entry.grid(row=14, column=1, padx=5, pady=5)
            elif selected_effect == "Distortion":
                self.drive_label.grid(row=13, column=0, sticky=tk.W, padx=5, pady=5)
                self.drive_entry.grid(row=13, column=1, padx=5, pady=5)

        def hide_effect_params(self):
            self.reverb_time_label.grid_forget()
            self.reverb_time_entry.grid_forget()
            self.decay_rate_label.grid_forget()
            self.decay_rate_entry.grid_forget()
            self.delay_label.grid_forget()
            self.delay_entry.grid_forget()
            self.decay_label.grid_forget()
            self.decay_entry.grid_forget()
            self.drive_label.grid_forget()
            self.drive_entry.grid_forget()

        def get_effect_params(self):
            effect_params = {}
            selected_effect = self.selected_effect.get()

            if selected_effect == "Reverb":
                try:
                    effect_params['reverb_time'] = float(self.reverb_time_entry.get()) if self.reverb_time_entry.get() else 0.5
                    effect_params['decay_rate'] = float(self.decay_rate_entry.get()) if self.decay_rate_entry.get() else 0.5
                except ValueError:
                    print("Invalid Reverb parameters. Using defaults.")
                    effect_params['reverb_time'] = 0.5
                    effect_params['decay_rate'] = 0.5
            elif selected_effect == "Echo":
                try:
                    effect_params['delay'] = float(self.delay_entry.get()) if self.delay_entry.get() else 0.2
                    effect_params['decay'] = float(self.decay_entry.get()) if self.decay_entry.get() else 0.6
                except ValueError:
                    print("Invalid Echo parameters. Using defaults.")
                    effect_params['delay'] = 0.2
                    effect_params['decay'] = 0.6
            elif selected_effect == "Distortion":
                try:
                    effect_params['drive'] = float(self.drive_entry.get()) if self.drive_entry.get() else 5.0
                except ValueError:
                    print("Invalid Distortion parameters. Using defaults.")
                    effect_params['drive'] = 5.0

            return effect_params

# Main Execution

if __name__ == "__main__":
    if GUI_ENABLED:
        root = tk.Tk()
        gui = AudioProcessorGUI(root)
        root.mainloop()
    else:
        print("GUI is disabled. Please install Tkinter to enable the GUI.")