###########################################################################
#
# Minimal WAS Node Suite — WAS_Text_Multiline & WAS_Text_Load_Line_From_File only
#
# Extracted from WAS Node Suite by WASasquatch / Dr.Lt.Data
# MIT License — see original repo for full license text.
#
###########################################################################

import folder_paths as comfy_paths
import hashlib
import json
import os

# ---------------------------------------------------------------------------
# Console string helper
# ---------------------------------------------------------------------------

class cstr(str):
    class color:
        END = '\33[0m'
        BOLD = '\33[1m'
        ITALIC = '\33[3m'
        UNDERLINE = '\33[4m'
        BLINK = '\33[5m'
        BLINK2 = '\33[6m'
        SELECTED = '\33[7m'

        BLACK = '\33[30m'
        RED = '\33[31m'
        GREEN = '\33[32m'
        YELLOW = '\33[33m'
        BLUE = '\33[34m'
        VIOLET = '\33[35m'
        BEIGE = '\33[36m'
        WHITE = '\33[37m'

        BLACKBG = '\33[40m'
        REDBG = '\33[41m'
        GREENBG = '\33[42m'
        YELLOWBG = '\33[43m'
        BLUEBG = '\33[44m'
        VIOLETBG = '\33[45m'
        BEIGEBG = '\33[46m'
        WHITEBG = '\33[47m'

        GREY = '\33[90m'
        LIGHTRED = '\33[91m'
        LIGHTGREEN = '\33[92m'
        LIGHTYELLOW = '\33[93m'
        LIGHTBLUE = '\33[94m'
        LIGHTVIOLET = '\33[95m'
        LIGHTBEIGE = '\33[96m'
        LIGHTWHITE = '\33[97m'

        GREYBG = '\33[100m'
        LIGHTREDBG = '\33[101m'
        LIGHTGREENBG = '\33[102m'
        LIGHTYELLOWBG = '\33[103m'
        LIGHTBLUEBG = '\33[104m'
        LIGHTVIOLETBG = '\33[105m'
        LIGHTBEIGEBG = '\33[106m'
        LIGHTWHITEBG = '\33[107m'

        @staticmethod
        def add_code(name, code):
            if not hasattr(cstr.color, name.upper()):
                setattr(cstr.color, name.upper(), code)
            else:
                raise ValueError(f"'cstr' object already contains a code with the name '{name}'.")

    def __new__(cls, text):
        return super().__new__(cls, text)

    def __getattr__(self, attr):
        if attr.lower().startswith("_cstr"):
            code = getattr(self.color, attr.upper().lstrip("_cstr"))
            modified_text = self.replace(f"__{attr[1:]}__", f"{code}")
            return cstr(modified_text)
        elif attr.upper() in dir(self.color):
            code = getattr(self.color, attr.upper())
            modified_text = f"{code}{self}{self.color.END}"
            return cstr(modified_text)
        elif attr.lower() in dir(cstr):
            return getattr(cstr, attr.lower())
        else:
            raise AttributeError(f"'cstr' object has no attribute '{attr}'")

    def print(self, **kwargs):
        print(self, **kwargs)

# Message prefix colour codes
cstr.color.add_code("msg",     f"{cstr.color.BLUE}WAS Node Suite: {cstr.color.END}")
cstr.color.add_code("warning", f"{cstr.color.BLUE}WAS Node Suite {cstr.color.LIGHTYELLOW}Warning: {cstr.color.END}")
cstr.color.add_code("error",   f"{cstr.color.RED}WAS Node Suite {cstr.color.END}Error: {cstr.color.END}")

# ---------------------------------------------------------------------------
# Global path constants
# ---------------------------------------------------------------------------

NODE_FILE        = os.path.abspath(__file__)
MODELS_DIR       = comfy_paths.models_dir
WAS_SUITE_ROOT   = os.path.dirname(NODE_FILE)
WAS_CONFIG_DIR   = os.environ.get('WAS_CONFIG_DIR', WAS_SUITE_ROOT)
WAS_DATABASE     = os.path.join(WAS_CONFIG_DIR, 'was_suite_settings.json')
WAS_HISTORY_DATABASE = os.path.join(WAS_CONFIG_DIR, 'was_history.json')

# ---------------------------------------------------------------------------
# WASDatabase — lightweight JSON key-value store
# ---------------------------------------------------------------------------

class WASDatabase:
    """
    Simple flat-file key-value database backed by JSON.
    Each value is stored under a category + key pair.
    """
    def __init__(self, filepath):
        self.filepath = filepath
        try:
            with open(filepath, 'r') as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {}

    def catExists(self, category):
        return category in self.data

    def keyExists(self, category, key):
        return category in self.data and key in self.data[category]

    def insert(self, category, key, value):
        if not isinstance(category, str) or not isinstance(key, str):
            cstr("Category and key must be strings").error.print()
            return
        if category not in self.data:
            self.data[category] = {}
        self.data[category][key] = value
        self._save()

    def update(self, category, key, value):
        if category in self.data and key in self.data[category]:
            self.data[category][key] = value
            self._save()

    def updateCat(self, category, dictionary):
        self.data[category].update(dictionary)
        self._save()

    def get(self, category, key):
        return self.data.get(category, {}).get(key, None)

    def getDB(self):
        return self.data

    def insertCat(self, category):
        if not isinstance(category, str):
            cstr("Category must be a string").error.print()
            return
        if category in self.data:
            cstr(f"The database category '{category}' already exists!").error.print()
            return
        self.data[category] = {}
        self._save()

    def getDict(self, category):
        if category not in self.data:
            cstr(f"The database category '{category}' does not exist!").error.print()
            return {}
        return self.data[category]

    def delete(self, category, key):
        if category in self.data and key in self.data[category]:
            del self.data[category][key]
            self._save()

    def _save(self):
        try:
            with open(self.filepath, 'w') as f:
                json.dump(self.data, f, indent=4)
        except FileNotFoundError:
            cstr(f"Cannot save database to file '{self.filepath}'. "
                 "Storing the data in the object instead. Does the folder and node file have write permissions?").warning.print()
        except Exception as e:
            cstr(f"Error while saving JSON data: {e}").error.print()

# Module-level settings database singleton (used by TextFileLoader)
WDB = WASDatabase(WAS_DATABASE)

# ---------------------------------------------------------------------------
# Helper: record text file paths in the history database
# ---------------------------------------------------------------------------

def update_history_text_files(new_paths):
    HDB = WASDatabase(WAS_HISTORY_DATABASE)
    if HDB.catExists("History") and HDB.keyExists("History", "TextFiles"):
        saved_paths = HDB.get("History", "TextFiles")
        for path_ in saved_paths:
            if not os.path.exists(path_):
                saved_paths.remove(path_)
        if isinstance(new_paths, str):
            if new_paths in saved_paths:
                saved_paths.remove(new_paths)
            saved_paths.append(new_paths)
        elif isinstance(new_paths, list):
            for path_ in new_paths:
                if path_ in saved_paths:
                    saved_paths.remove(path_)
                saved_paths.append(path_)
        HDB.update("History", "TextFiles", saved_paths)
    else:
        if not HDB.catExists("History"):
            HDB.insertCat("History")
        if isinstance(new_paths, str):
            HDB.insert("History", "TextFiles", [new_paths])
        elif isinstance(new_paths, list):
            HDB.insert("History", "TextFiles", new_paths)

# ---------------------------------------------------------------------------
# Shared type constant
# ---------------------------------------------------------------------------

TEXT_TYPE = "STRING"

# ---------------------------------------------------------------------------
# Node: WAS_Text_Multiline
# ---------------------------------------------------------------------------

class WAS_Text_Multiline:
    def __init__(self):
        pass

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "text": ("STRING", {
                    "default": "",
                    "multiline": True,
                    "dynamicPrompts": True
                }),
            }
        }

    RETURN_TYPES = (TEXT_TYPE,)
    FUNCTION = "text_multiline"
    CATEGORY = "WAS Suite/Text"

    def text_multiline(self, text):
        import io
        new_text = []
        for line in io.StringIO(text):
            if not line.strip().startswith('#'):
                new_text.append(line.replace("\n", ''))
        new_text = "\n".join(new_text)
        return (new_text,)

# ---------------------------------------------------------------------------
# Node: WAS_Text_Load_Line_From_File
# ---------------------------------------------------------------------------

class WAS_Text_Load_Line_From_File:
    def __init__(self):
        self.HDB = WASDatabase(WAS_HISTORY_DATABASE)

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "file_path":       ("STRING", {"default": '',            "multiline": False}),
                "dictionary_name": ("STRING", {"default": '[filename]',  "multiline": False}),
                "label":           ("STRING", {"default": 'TextBatch',   "multiline": False}),
                "mode":            (["automatic", "index"],),
                "index":           ("INT",    {"default": 0, "min": 0, "step": 1}),
            },
            "optional": {
                "multiline_text": (TEXT_TYPE, {"forceInput": True}),
            }
        }

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        if kwargs['mode'] != 'index':
            return float("NaN")
        else:
            m = hashlib.sha256()
            if os.path.exists(kwargs['file_path']):
                with open(kwargs['file_path'], 'rb') as f:
                    m.update(f.read())
                return m.digest().hex()
            else:
                return False

    RETURN_TYPES  = (TEXT_TYPE, "DICT")
    RETURN_NAMES  = ("line_text", "dictionary")
    FUNCTION      = "load_file"
    CATEGORY      = "WAS Suite/Text"

    def load_file(self, file_path='', dictionary_name='[filename]', label='TextBatch',
                  mode='automatic', index=0, multiline_text=None):

        # --- inline text path ---
        if multiline_text is not None:
            lines = multiline_text.strip().split('\n')
            if mode == 'index':
                if index < 0 or index >= len(lines):
                    cstr(f"Invalid line index `{index}`").error.print()
                    return ('', {dictionary_name: []})
                line = lines[index]
            else:
                line_index = self.HDB.get('TextBatch Counters', label)
                if line_index is None:
                    line_index = 0
                line = lines[line_index % len(lines)]
                self.HDB.insert('TextBatch Counters', label, line_index + 1)
            return (line, {dictionary_name: lines})

        # --- file path ---
        if file_path == '':
            cstr("No file path specified.").error.print()
            return ('', {dictionary_name: []})

        if not os.path.exists(file_path):
            cstr(f"The path `{file_path}` specified cannot be found.").error.print()
            return ('', {dictionary_name: []})

        file_list = self.TextFileLoader(file_path, label)
        line, lines = None, []
        if mode == 'automatic':
            line, lines = file_list.get_next_line()
        elif mode == 'index':
            if index >= len(file_list.lines):
                index = index % len(file_list.lines)
            line, lines = file_list.get_line_by_index(index)

        if line is None:
            cstr("No valid line was found. The file may be empty or all lines have been read.").error.print()
            return ('', {dictionary_name: []})

        file_list.store_index()
        update_history_text_files(file_path)
        return (line, {dictionary_name: lines})

    # ------------------------------------------------------------------
    # Inner helper: manages per-label file position across executions
    # ------------------------------------------------------------------

    class TextFileLoader:
        def __init__(self, file_path, label):
            self.WDB = WDB
            self.file_path = file_path
            self.lines = []
            self.index = 0
            self.label = label
            self.load_file(file_path)

        def load_file(self, file_path):
            stored_file_path = self.WDB.get('TextBatch Paths',    self.label)
            stored_index     = self.WDB.get('TextBatch Counters', self.label)
            if stored_file_path != file_path:
                self.index = 0
                self.WDB.insert('TextBatch Counters', self.label, 0)
                self.WDB.insert('TextBatch Paths',    self.label, file_path)
            else:
                self.index = stored_index
            with open(file_path, 'r', encoding="utf-8", newline='\n') as file:
                self.lines = [line.strip() for line in file]

        def get_line_index(self):
            return self.index

        def set_line_index(self, index):
            self.index = index
            self.WDB.insert('TextBatch Counters', self.label, self.index)

        def get_next_line(self):
            if self.index >= len(self.lines):
                self.index = 0
            line = self.lines[self.index]
            self.index += 1
            if self.index == len(self.lines):
                self.index = 0
            cstr(f'{cstr.color.YELLOW}TextBatch{cstr.color.END} Index: {self.index}').msg.print()
            return line, self.lines

        def get_line_by_index(self, index):
            if index < 0 or index >= len(self.lines):
                cstr(f"Invalid line index `{index}`").error.print()
                return None, []
            self.index = index
            line = self.lines[self.index]
            cstr(f'{cstr.color.YELLOW}TextBatch{cstr.color.END} Index: {self.index}').msg.print()
            return line, self.lines

        def store_index(self):
            self.WDB.insert('TextBatch Counters', self.label, self.index)

# ---------------------------------------------------------------------------
# ComfyUI node registration
# ---------------------------------------------------------------------------

NODE_CLASS_MAPPINGS = {
    "Text Multiline":            WAS_Text_Multiline,
    "Text Load Line From File":  WAS_Text_Load_Line_From_File,
}
