# models.py
# The "things" in our program: Person, Patient, Clinician and Appointment.
#
# INHERITANCE: Patient and Clinician inherit from Person.
# ENCAPSULATION: attributes start with __ (private). They can only be read or
#                changed through methods (get_... / set_...) that check the data.

from datetime import datetime


# ---------- small checking functions ----------
def check_date(date_text):
    """Date must look like 2026-12-01. Returns the cleaned text."""
    try:
        return datetime.strptime(date_text.strip(), "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        raise ValueError("Date must be a real date in this format: YYYY-MM-DD")


def check_time(time_text):
    """Time must look like 09:30 (24 hour clock). Returns the cleaned text."""
    try:
        return datetime.strptime(time_text.strip(), "%H:%M").strftime("%H:%M")
    except ValueError:
        raise ValueError("Time must be in this format: HH:MM (example 14:30)")


# ---------- Person (parent class) ----------
class Person:
    def __init__(self, person_id, name, phone):
        self.__id = person_id
        self.__name = ""
        self.__phone = ""
        self.set_name(name)
        self.set_phone(phone)

    def get_id(self):
        return self.__id

    def get_name(self):
        return self.__name

    def set_name(self, name):
        name = name.strip()
        if len(name) < 2:
            raise ValueError("Name must have at least 2 letters.")
        self.__name = name.title()

    def get_phone(self):
        return self.__phone

    def set_phone(self, phone):
        phone = phone.strip()
        digits = phone.replace("+", "").replace(" ", "")
        if not digits.isdigit() or len(digits) < 9 or len(digits) > 15:
            raise ValueError("Phone must have 9 to 15 digits.")
        self.__phone = phone

    def to_dict(self):
        return {"id": self.__id, "name": self.__name, "phone": self.__phone}


# ---------- Patient (child of Person) ----------
class Patient(Person):
    def __init__(self, person_id, name, phone, date_of_birth):
        super().__init__(person_id, name, phone)
        self.__date_of_birth = ""
        self.set_date_of_birth(date_of_birth)

    def get_date_of_birth(self):
        return self.__date_of_birth

    def set_date_of_birth(self, date_of_birth):
        date_of_birth = check_date(date_of_birth)
        if date_of_birth > datetime.now().strftime("%Y-%m-%d"):
            raise ValueError("Date of birth cannot be in the future.")
        self.__date_of_birth = date_of_birth

    def to_dict(self):
        data = super().to_dict()
        data["date_of_birth"] = self.__date_of_birth
        return data

    def __str__(self):
        return (self.get_id() + " | " + self.get_name() + " | " +
                self.get_phone() + " | Born: " + self.__date_of_birth)


# ---------- Clinician (child of Person) ----------
class Clinician(Person):
    def __init__(self, person_id, name, phone, specialisation):
        super().__init__(person_id, name, phone)
        self.__specialisation = ""
        self.set_specialisation(specialisation)

    def get_specialisation(self):
        return self.__specialisation

    def set_specialisation(self, specialisation):
        specialisation = specialisation.strip()
        if len(specialisation) < 3:
            raise ValueError("Specialisation must have at least 3 letters.")
        self.__specialisation = specialisation.title()

    def to_dict(self):
        data = super().to_dict()
        data["specialisation"] = self.__specialisation
        return data

    def __str__(self):
        return (self.get_id() + " | " + self.get_name() + " | " +
                self.get_phone() + " | " + self.__specialisation)


# ---------- Appointment ----------
class Appointment:
    def __init__(self, appt_id, patient_id, clinician_id, date, time, purpose,
                 status="scheduled"):
        self.__id = appt_id
        self.__patient_id = patient_id
        self.__clinician_id = clinician_id
        self.__date = check_date(date)
        self.__time = check_time(time)
        purpose = purpose.strip()
        if len(purpose) < 3:
            raise ValueError("Purpose must have at least 3 letters.")
        self.__purpose = purpose
        if status not in ["scheduled", "completed", "cancelled"]:
            raise ValueError("Status must be scheduled, completed or cancelled.")
        self.__status = status

    # getters
    def get_id(self):
        return self.__id

    def get_patient_id(self):
        return self.__patient_id

    def get_clinician_id(self):
        return self.__clinician_id

    def get_date(self):
        return self.__date

    def get_time(self):
        return self.__time

    def get_purpose(self):
        return self.__purpose

    def get_status(self):
        return self.__status

    def is_active(self):
        return self.__status == "scheduled"

    # the status can only change through these methods
    def cancel(self):
        if not self.is_active():
            raise ValueError("Only scheduled appointments can be cancelled.")
        self.__status = "cancelled"

    def complete(self):
        if not self.is_active():
            raise ValueError("Only scheduled appointments can be completed.")
        self.__status = "completed"

    def reschedule(self, new_date, new_time):
        if not self.is_active():
            raise ValueError("Only scheduled appointments can be rescheduled.")
        self.__date = check_date(new_date)
        self.__time = check_time(new_time)

    def to_dict(self):
        return {"id": self.__id, "patient_id": self.__patient_id,
                "clinician_id": self.__clinician_id, "date": self.__date,
                "time": self.__time, "purpose": self.__purpose,
                "status": self.__status}

    def __str__(self):
        return (self.__id + " | " + self.__date + " " + self.__time + " | Patient " +
                self.__patient_id + " | Clinician " + self.__clinician_id + " | " +
                self.__purpose + " | " + self.__status.upper())
