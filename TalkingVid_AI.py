"""
This program creates a widget which will accept text input and sends it via the OpenAI API to
the OpenAI tts-1 model to convert text to speech. An audio stream is returned and saved to a mp3 file.
"""
__author__ = "Carsten Pathe"
__license__ = "GNU General Public License v3.0"


import tkinter as tk
from tkinter import ttk
from tkinter import filedialog, messagebox, scrolledtext
import threading
import os
import time

from openai import OpenAI
client = OpenAI()

class Text2SpeechGUI:

    def __init__(self, root):
        self.root = root
        self.root.title("Text Printer GUI with File Operations and Multi-line Input")

        # Initialize variables to hold text and the output file path
        self.input_text = ""
        self.output_file_path = ""

        # Create a frame for the widgets
        frame = ttk.Frame(self.root, padding="10")
        frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Label for descriptive text
        label = ttk.Label(frame, text="Please enter your text below:", font=('Calibri',12))
        label.grid(row=0, column=0, columnspan=2, sticky=tk.W)

        # Multi-line text input field with word wrap enabled
        self.text_input = scrolledtext.ScrolledText(frame, wrap=tk.WORD, height=10, width=120, font=('Cambria',12))
        self.text_input.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E))
        self.text_input.focus()

        # Load text file button
        load_text_button = ttk.Button(frame, text="Load Text File", command=self.on_load_file_clicked, width=20)
        load_text_button.grid(row=2, column=0, padx=10, pady=10)

        # Specify output file button
        save_file_button = ttk.Button(frame, text="Specify Output File", command=self.on_save_file_clicked, width=20)
        save_file_button.grid(row=2, column=1, padx=10, pady=10)

        # txt_2_speech button
        tts_button = ttk.Button(frame, text="Text2Speech", command=self.text2speech_clicked, width=20)
        tts_button.grid(row=2, column=2, padx=30, pady=10)

        # quit button
        quit_button = ttk.Button(frame, text="Quit", command=self.on_quit_clicked, width=20)
        quit_button.grid(row=2, column=3, padx=10, pady=10)

        # Label for descriptive text
        label = ttk.Label(frame, text="Options", font=('Calibri', 12, 'bold'))
        label.grid(row=3, column=0, columnspan=4, sticky=tk.W)

        label = ttk.Label(frame, text="Voice", font=('Calibri', 12))
        label.grid(row=4, column=0, columnspan=4, sticky=tk.W)

        # Radio buttons for voice type
        self.voice = tk.StringVar(value="onyx")

        rButton_femaleVoice = ttk.Radiobutton(frame, text="Female voice", variable=self.voice, value="alloy")
        rButton_femaleVoice.grid(row=5, column=0, padx=0, pady=0, sticky='w')

        rButton_maleVoice = ttk.Radiobutton(frame, text="Male voice   ", variable=self.voice, value="onyx")
        rButton_maleVoice.grid(row=6, column=0, padx=0, pady=0, sticky='w')    

        # Entry for sound speed
        ttk.Label(frame, text="Speech Speed (0.5-2.0):", font=('Calibri', 12)).grid(row=10, column=0, padx=0, pady=0, sticky=tk.W)
        self.speed_entry = ttk.Entry(frame)
        self.speed_entry.grid(row=11, column=0, padx=0, pady=0, sticky=tk.W)
        self.speed_entry.insert(0, "1.0")  # Default speed

    # When button "Specify Output File" was clicked
    def on_save_file_clicked(self):
        self.output_file_path = filedialog.asksaveasfilename(filetypes=[("mp3 files", "*.mp3"), ("All files", "*.*")])

    # When button "txt_2_speech" was clicked
    def text2speech_clicked(self):

        # Retrieve and validate speed value from entry field
        try:
            speed = float(self.speed_entry.get())
            if not (0.5 <= speed <= 2.0):
                messagebox.showerror("Error", "Speed must be between 0.5 and 2.0")
                return
        except ValueError:
            messagebox.showerror("Error", "Invalid speed value. Please enter a number.")
            return

        # Retrieve and validate text input from text input window
        self.input_text = self.text_input.get("1.0", tk.END).strip()

        if not self.input_text:
            messagebox.showerror("Error", "No text input!")
            return

        if not self.output_file_path:
            messagebox.showerror("Error", "No output file specified!")
            return

        # Start the process in a new thread to avoid blocking the GUI
        threading.Thread(target=self.process_text, daemon=True).start()

    # When button "Load Text File" was clicked
    def on_load_file_clicked(self):

        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "r") as file:
                text_content = file.read()
                # Display the loaded text in the text input field
                self.text_input.delete("1.0", tk.END)
                self.text_input.insert(tk.END, text_content)

    # Thread "process_text" (when button "txt_2_speech" was clicked)
    def process_text(self):

        # Get settings for voice speed
        try:
            speed = float(self.speed_entry.get())  # Assumed validation has already happened
        except ValueError:
            speed = 1.0  # Default to 1.0 if there's an error, though this should be caught earlier

        # Get values of radio buttons for voice type
        selected_voice = self.voice.get()
        print(f"Selected voice type: {selected_voice}")

        try:
            response = client.audio.speech.create(
                model="tts-1",
                voice=selected_voice,
                speed=speed,
                input=self.input_text
            )

            # Immediately after receiving the response, show a message.
            self.root.after(0, lambda: messagebox.showinfo("Response Received", "The audio response has been received and written to file."))

            speech_file_path = self.output_file_path
            response.stream_to_file(speech_file_path)
            print(f"Saving audio to: {speech_file_path}")

            txtName = speech_file_path.rsplit('.', 1)[0] + '.txt'
            print(f"Saving text input to: {txtName}")
            with open(txtName, "w") as file:
                file.write(self.input_text)

        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Failed to process the text: {e}"))

    def on_quit_clicked(self):
        root.destroy()

# Create the main window and run the application
root = tk.Tk()
app = Text2SpeechGUI(root)
root.mainloop()
