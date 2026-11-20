# clinic.py
# The Clinic class coordinates everything: it owns the lists of patients,
# clinicians and appointments, loads/saves them, and uses the AppointmentManager.

import os
from clinic_app.models import Patient, Clinician, Appointment
from clinic_app.storage import JSONStorage
from clinic_app.appointment_manager import AppointmentManager


# the "data" folder inside the project folder
DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")


def id_exists(items, item_id):
    """True if an object in the list already has this id."""
    for item in items:
        if item.get_id() == item_id:
            return True
    return False


def make_id(prefix, items):
    """Makes the next id, e.g. P001, P002 ..."""
    highest = 0
    for item in items:
        number = int(item.get_id()[1:])
        if number > highest:
            highest = number
    return prefix + str(highest + 1).zfill(3)


class Clinic:
    def __init__(self, data_folder=DATA_FOLDER):
        self.storage = JSONStorage(data_folder)
        self.patients = []
        self.clinicians = []
        self.appointments = []
        self.warnings = []
        self.manager = AppointmentManager(self.patients, self.clinicians, self.appointments)
        self.load_all()

    # ---------- loading and saving ----------
    def load_all(self):
        # Every record that is skipped is explained in self.warnings.
        # If a file had skipped records, we first copy it to <file>.backup
        # so the original data is never lost when we save again.
        skipped = []  # names of files that had skipped records

        for r in self.storage.load("patients.json"):
            try:
                patient = Patient(r["id"], r["name"], r["phone"], r["date_of_birth"])
            except (KeyError, ValueError, TypeError):
                self.warnings.append("Skipped a bad patient record: " + str(r))
                skipped.append("patients.json")
                continue
            if id_exists(self.patients, patient.get_id()):  # no duplicate ids
                self.warnings.append("Skipped patient with duplicate id " + patient.get_id() + ".")
                skipped.append("patients.json")
                continue
            self.patients.append(patient)

        for r in self.storage.load("clinicians.json"):
            try:
                clinician = Clinician(r["id"], r["name"], r["phone"], r["specialisation"])
            except (KeyError, ValueError, TypeError):
                self.warnings.append("Skipped a bad clinician record: " + str(r))
                skipped.append("clinicians.json")
                continue
            if id_exists(self.clinicians, clinician.get_id()):
                self.warnings.append("Skipped clinician with duplicate id " + clinician.get_id() + ".")
                skipped.append("clinicians.json")
                continue
            self.clinicians.append(clinician)

        patient_ids = [p.get_id() for p in self.patients]
        clinician_ids = [c.get_id() for c in self.clinicians]
        for r in self.storage.load("appointments.json"):
            try:
                appt = Appointment(r["id"], r["patient_id"], r["clinician_id"],
                                   r["date"], r["time"], r["purpose"], r["status"])
            except (KeyError, ValueError, TypeError):
                self.warnings.append("Skipped a bad appointment record: " + str(r))
                skipped.append("appointments.json")
                continue
            if id_exists(self.appointments, appt.get_id()):
                self.warnings.append("Skipped appointment with duplicate id " + appt.get_id() + ".")
                skipped.append("appointments.json")
                continue
            # keep references valid: patient and clinician must exist
            if appt.get_patient_id() not in patient_ids or appt.get_clinician_id() not in clinician_ids:
                self.warnings.append("Skipped appointment " + appt.get_id() +
                                     " (patient or clinician not found).")
                skipped.append("appointments.json")
                continue
            self.appointments.append(appt)

        for filename in set(skipped):
            self.storage.backup(filename)
            self.warnings.append("A copy of " + filename + " was saved as " + filename + ".backup")

        self.warnings.extend(self.storage.messages)

    def save_all(self):
        self.storage.save("patients.json", [p.to_dict() for p in self.patients])
        self.storage.save("clinicians.json", [c.to_dict() for c in self.clinicians])
        self.storage.save("appointments.json", [a.to_dict() for a in self.appointments])

    # ---------- patients ----------
    def add_patient(self, name, phone, date_of_birth):
        new_patient = Patient(make_id("P", self.patients), name, phone, date_of_birth)
        for p in self.patients:  # prevent duplicates
            if (p.get_name() == new_patient.get_name() and
                    p.get_date_of_birth() == new_patient.get_date_of_birth()):
                raise ValueError("This patient is already registered as " + p.get_id() + ".")
        self.patients.append(new_patient)
        self.save_all()
        return new_patient

    def find_patient(self, patient_id):
        for p in self.patients:
            if p.get_id() == patient_id.strip().upper():
                return p
        raise ValueError("Patient " + patient_id + " does not exist.")

    def search_patients(self, text):
        text = text.strip().lower()
        return [p for p in self.patients
                if text in p.get_name().lower() or text == p.get_id().lower()]

    def update_patient(self, patient_id, name, phone, date_of_birth):
        """Empty text means 'keep the old value'."""
        patient = self.find_patient(patient_id)
        if name != "":
            patient.set_name(name)
        if phone != "":
            patient.set_phone(phone)
        if date_of_birth != "":
            patient.set_date_of_birth(date_of_birth)
        self.save_all()
        return patient

    # ---------- clinicians ----------
    def add_clinician(self, name, phone, specialisation):
        new_clinician = Clinician(make_id("C", self.clinicians), name, phone, specialisation)
        self.clinicians.append(new_clinician)
        self.save_all()
        return new_clinician

    def find_clinician(self, clinician_id):
        for c in self.clinicians:
            if c.get_id() == clinician_id.strip().upper():
                return c
        raise ValueError("Clinician " + clinician_id + " does not exist.")

    def search_clinicians(self, text):
        text = text.strip().lower()
        return [c for c in self.clinicians
                if text in c.get_name().lower() or text in c.get_specialisation().lower()
                or text == c.get_id().lower()]

    def update_clinician(self, clinician_id, name, phone, specialisation):
        clinician = self.find_clinician(clinician_id)
        if name != "":
            clinician.set_name(name)
        if phone != "":
            clinician.set_phone(phone)
        if specialisation != "":
            clinician.set_specialisation(specialisation)
        self.save_all()
        return clinician

    # ---------- appointments: use the manager, then save ----------
    def schedule(self, patient_id, clinician_id, date, time, purpose):
        appt = self.manager.schedule(patient_id, clinician_id, date, time, purpose)
        self.save_all()
        return appt

    def reschedule(self, appt_id, new_date, new_time):
        appt = self.manager.reschedule(appt_id, new_date, new_time)
        self.save_all()
        return appt

    def cancel(self, appt_id):
        appt = self.manager.cancel(appt_id)
        self.save_all()
        return appt

    def complete(self, appt_id):
        appt = self.manager.complete(appt_id)
        self.save_all()
        return appt
