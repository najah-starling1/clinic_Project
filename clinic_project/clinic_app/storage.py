# storage.py
# JSONStorage only reads and writes JSON files. It knows nothing about patients.

import json
import os
import shutil


class JSONStorage:
    def __init__(self, folder="data"):
        self.folder = folder
        os.makedirs(folder, exist_ok=True)
        self.messages = []  # warnings to show the user at start up

    def load(self, filename):
        """Returns a list of records. Never crashes on a bad file."""
        path = os.path.join(self.folder, filename)

        if not os.path.exists(path):  # file is missing
            self.messages.append(filename + " was missing, so a new empty one was made.")
            self.save(filename, [])
            return []

        with open(path, "r") as file:
            text = file.read()

        if text.strip() == "":  # file is empty
            return []

        try:
            data = json.loads(text)
        except json.JSONDecodeError:  # file is broken
            self.messages.append(filename + " is damaged. Starting with no records. "
                                 "(Old file saved as " + filename + ".broken)")
            os.replace(path, path + ".broken")
            return []

        if not isinstance(data, list):
            self.messages.append(filename + " has the wrong format. Starting with no records.")
            return []
        return data

    def backup(self, filename):
        """Copies a file to filename.backup so nothing is lost for good."""
        path = os.path.join(self.folder, filename)
        if os.path.exists(path):
            shutil.copy(path, path + ".backup")

    def save(self, filename, records):
        path = os.path.join(self.folder, filename)
        with open(path, "w") as file:
            json.dump(records, file, indent=2)
