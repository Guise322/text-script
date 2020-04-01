import glib
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox


class Gui:

    def __init__(self, _word_catcher, _log, _setup):

        # Creates instance wide log object
        self._log = _log.log
        self._log.debug("Gui: Starting Gui initialization.")

        # Imports WordCatcher object initialized in text-script
        self._word_catcher = _word_catcher

        # Imports Setup object initialized in text-script
        self._setup = _setup

        # Sends the self object to TextController so the Tkinter window can be closed
        self._word_catcher.set_gui(self)

        # Initialize root in __init__
        self._root = None

        # Threading event: used for communication between threads
        self._stop_event = threading.Event()

        # Global GUI settings
        self._global_categories = "Helvetica 12 bold"
        self._global_labels = "Helvetica"
        self._global_bold = "Helvetica 10 bold"

        # Sets up the window layout
        self._setup_window()

        # Starts WordCatcher listener
        self._start_word_catcher()
        self._log.debug("Gui: WordCatcher started successfully.")

        # Close program if window is destroyed
        self._root.protocol("WM_DELETE_WINDOW", self._on_closing)

        # Starts the window loop
        self._log.debug("Starting root mainloop.")
        self._root.mainloop()

    def _setup_window(self):
        """
        Window Setup
        """

        self._log.debug("Gui: Setting up root window.")

        # Creates the root window
        self._root = tk.Tk()

        # Sets the window corner icon
        self._root.iconbitmap(default='../assets/textscript.ico')

        # Window title
        self._root.title("Text-Script")

        # Window size
        self._root.geometry("400x400")

        # Create menu
        self._create_menu()

        self._log.debug("Root window setup successfully.")

    def _create_menu(self):

        # Create menu object
        _menu = tk.Menu(self._root)
        self._root.config(menu=_menu)
        self._log.debug("Gui: Successfully created top menu.")

        # File menu
        _file_menu = tk.Menu(_menu, tearoff=False)
        _menu.add_cascade(label="File", underline=0, menu=_file_menu)

        # File Menu
        _file_menu.add_command(
            label="Settings",
            command=self._open_settings
        )
        _file_menu.add_command(
            label="Quit",
            underline=0,
            command=self.close_text_script,
            accelerator="Ctrl+Q"
        )

        # Help Menu
        _help_menu = tk.Menu(_menu, tearoff=False)
        _menu.add_cascade(label="Help", underline=0, menu=_help_menu)

        # Help Menu
        _help_menu.add_command(
            label="How to Use",
            command=self._open_help
        )
        _help_menu.add_command(
            label="Documentation",
            command=self._open_documentation
        )

        # Shortcuts for menu options
        self._root.bind_all("<Control-q>", self.close_text_script)
        self._root.bind_all("<Control-h>", self._do_nothing())

    def _open_settings(self):
        """
        Opens a window with the available settings. Alters the config file.
        """

        # Get the directories from config file
        _directories = self._setup.find_directories()

        # Sets the entry values
        if (_directories[0] is None) or (len(_directories[0]) == 0):
            _current_default = "Not Set"
        else:
            _current_default = _directories[0]

        if (_directories[1] is None) or (len(_directories[1]) == 0):
            _current_local = "Not Set"
        else:
            _current_local = _directories[1]

        if (_directories[2] is None) or (len(_directories[2]) == 0):
            _current_remote = "Not Set"
        else:
            _current_remote = _directories[2]

        """
        Create Window
        """

        # Creates a new window
        self._settings_window = tk.Tk()

        # Window Setup
        self._settings_window.title("Settings")
        self._settings_window.iconbitmap(default='../assets/textscript.ico')  # Sets the window corner icon

        """
        Create Widgets
        """

        # Static Labels
        _directories_label = tk.Label(
            self._settings_window,
            justify="left",
            text="DIRECTORIES",
            font=self._global_categories
        )
        _default_label = tk.Label(
            self._settings_window,
            justify="left",
            text="Default Directory: "
        )
        _local_label = tk.Label(
            self._settings_window,
            justify="left",
            text="Local Directory: "
        )
        _remote_label = tk.Label(
            self._settings_window,
            justify="left",
            text="Remote Directory: ",
        )
        # Save Result Label - shows the result of self._save_settings
        self._save_result = tk.Label(
            self._settings_window,
            justify="left",
            fg="red",
            font=self._global_bold,
            text=""
        )

        # TK StringVars (required to change text of entry fields automatically)
        # Entry
        self._default_sv = tk.StringVar(self._settings_window, value=_current_default)
        self._local_sv = tk.StringVar(self._settings_window, value=_current_local)
        self._remote_sv = tk.StringVar(self._settings_window, value=_current_remote)

        # Directory Entry Fields
        self._default_entry = tk.Entry(
            self._settings_window,
            justify="left",
            width=45,
            textvariable=self._default_sv,
        )
        self._local_entry = tk.Entry(
            self._settings_window,
            justify="left",
            width=45,
            textvariable=self._local_sv,
        )
        self._remote_entry = tk.Entry(
            self._settings_window,
            justify="left",
            width=45,
            textvariable=self._remote_sv,
        )

        # Buttons
        # Default
        _btn_enable_default = tk.Button(
            self._settings_window,
            width=11,
            text="Enable",
            command=self._enable_default
        )
        _btn_disable_default = tk.Button(
            self._settings_window,
            width=11,
            text="Disable",
            command=self._disable_default
        )
        # Local
        _btn_set_local = tk.Button(
            self._settings_window,
            width=11,
            text="Set",
            command=self._set_local
        )
        _btn_disable_local = tk.Button(
            self._settings_window,
            width=11,
            text="Disable",
            command=self._disable_local
        )
        # Remote
        _btn_set_remote = tk.Button(
            self._settings_window,
            width=11,
            text="Set",
            command=self._set_remote
        )
        _btn_disable_remote = tk.Button(
            self._settings_window,
            width=11,
            text="Disable",
            command=self._disable_remote
        )
        # Save
        _btn_save = tk.Button(
            self._settings_window,
            width=11,
            text="Save",
            command=self._save_settings
        )

        # Pack Widgets
        # Description Labels
        _directories_label.grid(row=0, column=0, sticky="w", padx=4, pady=2)
        _default_label.grid(row=1, column=0, sticky="w", padx=4, pady=2)
        _local_label.grid(row=2, column=0, sticky="w", padx=4, pady=2)
        _remote_label.grid(row=3, column=0, sticky="w", padx=4, pady=2)
        # Entry Fields
        self._default_entry.grid(row=1, column=1, sticky="w", padx=4, pady=2)
        self._local_entry.grid(row=2, column=1, sticky="w", padx=4, pady=2)
        self._remote_entry.grid(row=3, column=1, sticky="w", padx=4, pady=2)
        # Buttons
        _btn_enable_default.grid(row=1, column=2, sticky="w", padx=4, pady=2)
        _btn_disable_default.grid(row=1, column=3, sticky="w", padx=4, pady=2)
        _btn_set_local.grid(row=2, column=2, sticky="w", padx=4, pady=2)
        _btn_disable_local.grid(row=2, column=3, sticky="w", padx=4, pady=2)
        _btn_set_remote.grid(row=3, column=2, sticky="w", padx=4, pady=2)
        _btn_disable_remote.grid(row=3, column=3, sticky="w", padx=4, pady=2)
        _btn_save.grid(row=4, column=3, sticky="w", padx=4, pady=2)
        # Save Result
        self._save_result.grid(row=4, column=1, sticky="w", padx=4, pady=2)

    def _enable_default(self):
        """
        Sets the default directory
        """

        self._default_sv.set("./textblocks/")
        self._save_result['text'] = ""

    def _disable_default(self):
        """
        Disables the default directory
        """

        self._default_sv.set("Not Set")
        self._save_result['text'] = ""

    def _set_local(self):
        """
        Sets local directory
        """

        # Uses askdirectory to set the directory
        self._local_sv.set(filedialog.askdirectory())
        self._save_result['text'] = ""

    def _disable_local(self):
        """
        Disables the local directory
        """

        self._local_sv.set("Not Set")
        self._save_result['text'] = ""

    def _set_remote(self):
        """
        Save remote directory
        """

        # Uses askdirectory to set the directory
        self._remote_sv.set(filedialog.askdirectory())
        self._save_result['text'] = ""

    def _disable_remote(self):
        """
        Disables the remote directory
        """

        self._remote_sv.set("Not Set")
        self._save_result['text'] = ""

    def _save_settings(self):
        """
        Overwrites the directories in the config file
        """

        # Initialize Variables
        _save_successful = False  # Variable that tracks if save was successful

        # Gets the values from the entry fields
        _default = self._default_entry.get()
        _local = self._local_entry.get()
        _remote = self._remote_entry.get()

        _real_dirs = True  # Tracks if all directories are real before saving
        _error_message = ""

        # Sets values to None if Not Set
        if _default == "Not Set":
            _default = "None"
        if _local == "Not Set":
            _local = "None"
        if _remote == "Not Set":
            _remote = "None"

        _directories = [_default, _local, _remote]  # List of directories

        for _directory in _directories:  # For each directory

            if _directory != "None":
                _exists = glib.check_directory(_directory)  # Check if the directory exists

                if _exists is False:  # If doesn't exist
                    _real_dirs = False  # Set _real_dirs to false, else leave it True
                    _error_message += f"Invalid directory: {_directory}\n"

        if _real_dirs is False:
            messagebox.showinfo("Save settings failed", _error_message)
        else:
            # Writes to config
            print(f"Saving directories: {_default}, {_local}, {_remote}")
            _save_successful = self._setup.save_settings(_directories)

        if _save_successful is True:
            self._word_catcher.reload_shortcuts(called_externally=True)
            self._save_result['text'] = "Save Successful"

    def _open_help(self):
        """
        Opens a window with the Text-Script Instructions
        """

        # Help text
        _help_text = glib.help_text()

        # Creates a new window
        self._help_window = tk.Tk()

        # Window Setup
        self._help_window.title("How to use Text-Script")
        self._help_window.iconbitmap(default='../assets/textscript.ico')  # Sets the window corner icon

        # Labels
        _help_label = tk.Label(
            self._help_window,
            justify="left",
            text=_help_text,
        )

        # Packs labels into window
        _help_label.grid(row=0, column=0, sticky="w", padx=4, pady=2)

    def _open_documentation(self):
        """
        Shows the user the link to the documentation and offers to open this in browser. Selecting no closes the window.
        """

        # Repository URL
        self._documentation_url = "https://github.com/GeorgeCiesinski/text-script"

        # Label for documentation window
        _documentation_message = f"""You can find the documentation at the below link: 

{self._documentation_url}

"""

        # Creates a new window
        self._doc_window = tk.Tk()

        # Window setup
        self._doc_window.title("Text-Script Documentation")
        self._doc_window.iconbitmap(default='../assets/textscript.ico')  # Sets the window corner icon
        self._doc_window.geometry("310x130")

        # Create Labels
        _link_label = tk.Label(
            self._doc_window,
            justify="left",
            text=_documentation_message
        )

        # Create Buttons
        _open_link = tk.Button(
            self._doc_window,
            text="Open Link",
            width=11,
            height=1,
            bd=4,
            command=self._open_link
        )

        # Packs widgets into window
        # Labels
        _link_label.grid(row=1, column=0, padx=4, pady=2)
        # Buttons
        _open_link.grid(row=2, column=0)

    def _open_link(self):
        """
        Opens documentation link in default browser.
        """

        # Opens link after user presses yes. Opens as a tab and raises the window
        webbrowser.open(self._documentation_url, new=0, autoraise=True)

        # Calls function to close window
        self._close_window()

    def _close_window(self):
        """
        Destroys the documentation window.
        """

        self._doc_window.destroy()

    def _do_nothing(self):
        """
        Temporary placeholder function. To be removed once GUI elements are complete.
        """

        pass

    def _start_word_catcher(self):
        """
        Starts listener as a new thread
        """

        self._log.debug("Gui: Starting Word Catcher.")

        word_catcher_thread = self._start_thread(target=self._word_catcher.run_listener)

    def _start_thread(self, target):
        """
        Starts target as a new thread
        """

        self._log.debug("Gui: Starting new thread.")

        self._stop_event.clear()
        thread = threading.Thread(target=target)
        thread.start()
        return thread

    def _on_closing(self):
        """
        Closes program if user clicks x button on the window
        """

        self._log.debug("User clicked the x button. Quiting program.")
        self.close_text_script()

    def close_text_script(self, event=None):
        """
        Kills the GUI. Can be called from outside Gui so Listener can kill it.
        """

        self._word_catcher.stop_listener()
        self._log.debug("Gui: Listener stopped successfully. Destroying the window.")
        self._root.destroy()
