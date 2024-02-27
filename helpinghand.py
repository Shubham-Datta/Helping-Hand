import tkinter
import customtkinter
import speech_recognition as sr
from tkinter import filedialog
import pytesseract
from fpdf import FPDF
import PyPDF2
import re
from textblob import TextBlob
import pyttsx3
from tkinter import messagebox
import threading
from translate import Translator
from PyDictionary import PyDictionary
from langdetect import detect

from PyInstaller.utils.hooks import collect_data_files,collect_submodules

#should only require hiddenimports
#datas = collect_data_files('pyaudio')
hiddenimports = collect_submodules('pyaudio')

customtkinter.set_appearance_mode("System")  # Modes: "System" (standard), "Dark", "Light"
customtkinter.set_default_color_theme("blue")  # Themes: "blue" (standard), "green", "dark-blue"

class App(customtkinter.CTk):
    global start_frame, file_name_entry, text_entry, text_var

    def __init__(self):
        super().__init__()
        

        # Create a new customtkinter window
        self.window = customtkinter.CTk()

        # configure window
        self.title("Helping Hand")
        self.window.geometry(f"{1100}x{580}")

        # Create the frames and pack them into the main window
        self.start_frame = customtkinter.CTkFrame(self.window)

        #self.options_frame = customtkinter.CTkFrame(self.window)

        # Pack the start frame into the main window
        self.start_frame.pack(fill=tkinter.BOTH, expand=True)

        # configure grid layout (4x4)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure((2, 3), weight=0)
        self.grid_rowconfigure((0, 1, 2, 3, 4, 5, 6, 7, 8), weight=1)

        # create sidebar frame with widgets
        self.sidebar_frame = customtkinter.CTkFrame(self, width=500, corner_radius=10)
        self.sidebar_frame.grid(row=0, column=0, rowspan= 8, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(4, weight=1)
        self.file_name_entry = customtkinter.CTkEntry(self.sidebar_frame, placeholder_text="Enter File Name")
        self.file_name_entry.grid(row=0, column=0, padx=20, pady=(20, 10))
        self.sidebar_button_1 = customtkinter.CTkButton(self.sidebar_frame, text="Create New File", command=self.create_file)
        self.sidebar_button_1.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.sidebar_frame, text="Open File", command=self.open_file)
        self.sidebar_button_2.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.sidebar_frame, text="Convert PDF to Text", command=self.convert_pdf_to_text)
        self.sidebar_button_3.grid(row=3, column=0, padx=20, pady=10)
        self.word_info_button = customtkinter.CTkButton(self.sidebar_frame, text="Word Info", command=self.show_word_info)
        self.word_info_button.grid(row=4, column=0, padx=20, pady=10) 
        self.appearance_mode_label = customtkinter.CTkLabel(self.sidebar_frame, text="Appearance Mode:", anchor="w")
        self.appearance_mode_label.grid(row=5, column=0, padx=20, pady=(10, 0))
        self.appearance_mode_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["Light", "Dark", "System"],
                                                                       command=self.change_appearance_mode_event)
        self.appearance_mode_optionemenu.grid(row=6, column=0, padx=20, pady=(10, 10))
        self.scaling_label = customtkinter.CTkLabel(self.sidebar_frame, text="UI Scaling:", anchor="w")
        self.scaling_label.grid(row=7, column=0, padx=20, pady=(10, 0))
        self.scaling_optionemenu = customtkinter.CTkOptionMenu(self.sidebar_frame, values=["80%", "100%", "120%", "150%", "170%"],
                                                               command=self.change_scaling_event)
        self.scaling_optionemenu.grid(row=8, column=0, padx=20, pady=(10, 20))

        # Create a label for the text
        self.title_label = customtkinter.CTkLabel(self, text="HELPING HAND", font=customtkinter.CTkFont(size=50, weight="bold"))
        self.title_label.grid(row=0, column=1, padx=(10, 10), pady=(5, 0))

        # create textbox
        self.textbox = customtkinter.CTkTextbox(self, width=250)
        self.textbox.grid(row=1, column=1, rowspan=7, padx=(10, 10), pady=(5, 5), sticky="nsew")

        # create rightside sidebar frame
        self.right_sidebar_frame = customtkinter.CTkFrame(self)
        self.right_sidebar_frame.grid_rowconfigure(6, weight=1)
        self.right_sidebar_frame.grid(row=0, column=3, rowspan=8, padx=(0, 0), pady=(20, 0), sticky="nsew")
        self.sidebar_button_1 = customtkinter.CTkButton(self.right_sidebar_frame, text="Start Speech Recognition", command=self.start_speech_recognition)
        self.sidebar_button_1.grid(row=0, column=0, padx=20, pady=10)
        self.sidebar_button_2 = customtkinter.CTkButton(self.right_sidebar_frame, text="Convert Image to Text", command=self.convert_image_to_text)
        self.sidebar_button_2.grid(row=1, column=0, padx=20, pady=10)
        self.sidebar_button_3 = customtkinter.CTkButton(self.right_sidebar_frame, text="Save Text", command=self.save_text)
        self.sidebar_button_3.grid(row=2, column=0, padx=20, pady=10)
        self.sidebar_button_4 = customtkinter.CTkButton(self.right_sidebar_frame, text="Convert to PDF", command=self.convert_to_pdf)
        self.sidebar_button_4.grid(row=3, column=0, padx=20, pady=10)
        self.sidebar_button_5 = customtkinter.CTkButton(self.right_sidebar_frame, text="Correct Spelling", command=self.correct_spelling)
        self.sidebar_button_5.grid(row=4, column=0, padx=20, pady=10)
        self.sidebar_button_6 = customtkinter.CTkButton(self.right_sidebar_frame, text="Convert Text to Voice", command=self.convert_text_to_speech)
        self.sidebar_button_6.grid(row=5, column=0, padx=20, pady=10)

        # Create a variable to hold the selected language
        self.selected_language = customtkinter.StringVar(value="English")  # set initial value


        # Create a dictionary to map language names to their respective codes
        self.languages = {"English": "en", "Hindi": "hi", "Bengali": "bn", "Marathi": "mr", "Tamil": "ta"}

        # Create the dropdown menu
        self.language_optionmenu = customtkinter.CTkComboBox(master=self.right_sidebar_frame, values=list(self.languages.keys()), variable=self.selected_language)
        self.language_optionmenu.grid(row=9, column=0, padx=20, pady=10)

        # Create the translate button
        self.translate_button = customtkinter.CTkButton(self.right_sidebar_frame, text="Translate", command=lambda: self.translate_text(self.selected_language.get()))
        self.translate_button.grid(row=10, column=0, padx=20, pady=10) 


        # set default values
        self.appearance_mode_optionemenu.set("System")
        self.scaling_optionemenu.set("100%")


    def change_appearance_mode_event(self, new_appearance_mode: str):
        customtkinter.set_appearance_mode(new_appearance_mode)

    def change_scaling_event(self, new_scaling: str):
        new_scaling_float = int(new_scaling.replace("%", "")) / 100
        customtkinter.set_widget_scaling(new_scaling_float)

    def create_file(self):
        file_name = self.file_name_entry.get()
        open(file_name, "w").close()
        self.textbox.delete("1.0", tkinter.END)
        messagebox.showinfo("Success", "File created successfully!")

        
    def open_file(self):
        try:
            file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt")])
            with open(file_path, "r", encoding='utf-8') as file:
                text = file.read()
            self.textbox.delete("1.0", tkinter.END)
            self.textbox.insert(tkinter.END, text)
            self.file_name_entry.delete(0, tkinter.END)
            self.file_name_entry.insert(0, file_path)
        except FileNotFoundError:
            messagebox.showerror("Error", "The file does not exist.")
        except PermissionError:
            messagebox.showerror("Error", "You do not have permission to open this file.")
        except Exception as e:
            messagebox.showerror("Error", str(e))


    def start_speech_recognition(self):
        threading.Thread(target=self._start_speech_recognition).start()

    def _start_speech_recognition(self):
        r = sr.Recognizer()
        with sr.Microphone() as source:
            r.adjust_for_ambient_noise(source)
            audio = r.listen(source)
        try:
            text = r.recognize_google(audio)
            self.textbox.delete("1.0", tkinter.END)
            self.textbox.insert(tkinter.END, text)
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def convert_image_to_text(self):
        # Set the path to the tesseract executable
        pytesseract.pytesseract.tesseract_cmd = r'TesseractOCR\tesseract.exe'

        # Open a file dialog and get the path of the selected image file
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.jpg;*.png;*.bmp")])

        # Extract text from the image
        text = pytesseract.image_to_string(file_path)

        # Set the text in the Text widget
        self.textbox.delete("1.0", tkinter.END)
        self.textbox.insert(tkinter.END, text)

    def save_text(self):
        file_name = self.file_name_entry.get()
        if not file_name.endswith(".txt"):
            messagebox.showerror("Error", "Invalid file type. Please enter a .txt file.")
            return
        text = self.textbox.get("1.0", tkinter.END)
        with open(file_name, "w", encoding='utf-8') as f:  # specify 'utf-8' encoding
            f.write(text + "\n")


    def translate_text(self, choice):
        # Get the text from the Text widget
        text = self.textbox.get("1.0", tkinter.END)

        # Create a Translator object for English
        translator_to_english = Translator(to_lang="en")

        # Translate the text to English
        text_in_english = translator_to_english.translate(text)

        # Get the target language code from the selected language
        target_language = self.languages[choice]

        # Create a Translator object for the target language
        translator_to_target = Translator(to_lang=target_language)

        # Translate the English text to the target language
        translated_text = translator_to_target.translate(text_in_english)

        # Set the translated text in the Text widget
        self.textbox.delete("1.0", tkinter.END)
        self.textbox.insert(tkinter.END, translated_text)

    def convert_to_pdf(self):
        # Get the file name from the entry
        file_name = self.file_name_entry.get()

        # Create a new FPDF object
        pdf = FPDF()

        # Add a page to the PDF
        pdf.add_page()

        # Add a Unicode-compatible font to the PDF
        # Make sure the font file supports Hindi characters
        pdf.add_font("DejaVu", "", "Fonts\\DejaVuSansCondensed.ttf", uni=True)

        # Set the font for the PDF
        pdf.set_font("DejaVu", size=14)

        # Open the text file and read its contents
        with open(file_name, "r", encoding='utf-8') as f:  # specify 'utf-8' encoding
            text = f.read()

            # Split the text into paragraphs
            paragraphs = text.split('\n')

            for paragraph in paragraphs:
                # Add each paragraph to the PDF and add a line break
                pdf.multi_cell(0, 10, txt=paragraph)
                pdf.ln(5)  # Reduce the line height to reduce space between paragraphs

        # Save the PDF file with the same name as the text file but with a .pdf extension
        pdf.output(file_name.replace(".txt", ".pdf"))



    def convert_pdf_to_text(self):
        # Open a file dialog and get the path of the selected PDF file
        file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])

        # Open the PDF file in read-binary mode
        with open(file_path, "rb") as file:
            # Create a PDF file reader object
            pdf_reader = PyPDF2.PdfReader(file)

            # Initialize an empty string to hold the extracted text
            text = ""

            # Loop through each page in the PDF and extract the text
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text()

        # Remove extra line breaks
        text = re.sub('\n+', '\n', text)

        # Set the text in the Text widget
        self.textbox.delete("1.0", tkinter.END)
        self.textbox.insert(tkinter.END, text)

        # Save the extracted text to a file with the same name as the PDF file but with a .txt extension
        txt_file_path = file_path.replace(".pdf", ".txt")
        with open(txt_file_path, "w", encoding="utf-8") as txt_file:
            txt_file.write(text)

    def correct_spelling(self):
        # Get the text from the Text widget
        text = self.textbox.get("1.0", tkinter.END)

        # Check if the filename is empty
        if not text:
            messagebox.showerror("Error", "No file selected.")
            return

        # Create a TextBlob object
        blob = TextBlob(text)

        # Correct the spelling of the text
        corrected_text = str(blob.correct())

        # Set the corrected text in the Text widget
        self.textbox.delete("1.0", tkinter.END)
        self.textbox.insert(tkinter.END, corrected_text)

        # Get the file name from the entry
        file_name = self.file_name_entry.get()

        # Save the corrected text to the same file as the original text
        with open(file_name, "w") as f:
            f.write(corrected_text)

    def convert_text_to_speech(self):
        threading.Thread(target=self._convert_text_to_speech).start()

    def _convert_text_to_speech(self):
        # Initialize the speech synthesis engine
        engine = pyttsx3.init()

        # Get the text from the Text widget
        text = self.textbox.get("1.0", tkinter.END)

        # Detect the language of the text
        language = detect(text)

        # Check if the language is English
        if language != 'en':
            messagebox.showerror("Error", "The text-to-speech conversion only supports English text.")
            return

        # Save the speech audio into a file
        file_path = filedialog.asksaveasfilename(defaultextension=".mp3", filetypes=[("MP3 files", "*.mp3")])

        # Save the speech audio into a file
        engine.save_to_file(text, file_path)

        # Blocking call to start the speech synthesis
        engine.runAndWait()

        # Play the speech audio
        engine.say(text)
        engine.runAndWait()


    def show_word_info(self):
        try:
            # Get the selected word from the Text widget
            word = self.textbox.selection_get()
        except tkinter.TclError:
            messagebox.showerror("Error", "No word selected.")
            return

        # Create a PyDictionary object
        dictionary = PyDictionary()

        # Get the meaning, synonyms, and antonyms of the word
        try:
            meaning = dictionary.meaning(word)
            synonyms = dictionary.synonym(word)
            antonyms = dictionary.antonym(word)
        except Exception as e:
            messagebox.showerror("Error", str(e))
            return

        # Create a new window to display the word info
        info_window = customtkinter.CTkToplevel(self)
        info_window.title(f"Info for {word}")

        # Bring the new window to the front
        info_window.lift()
        info_window.attributes('-topmost', True)

        # Add labels to the window to display the word info
        meaning_label = customtkinter.CTkLabel(info_window, text=f"Meaning: {meaning}", wraplength=500)
        meaning_label.pack()

        # Check if synonyms and antonyms are None and display a message accordingly
        if synonyms is None:
            synonyms_label = customtkinter.CTkLabel(info_window, text="Synonyms: No synonyms found", wraplength=500)
        else:
            synonyms_label = customtkinter.CTkLabel(info_window, text=f"Synonyms: {synonyms}", wraplength=500)
        synonyms_label.pack()

        if antonyms is None:
            antonyms_label = customtkinter.CTkLabel(info_window, text="Antonyms: No antonyms found", wraplength=500)
        else:
            antonyms_label = customtkinter.CTkLabel(info_window, text=f"Antonyms: {antonyms}", wraplength=500)
        antonyms_label.pack()



if __name__ == "__main__":
    app = App()
    app.mainloop()
