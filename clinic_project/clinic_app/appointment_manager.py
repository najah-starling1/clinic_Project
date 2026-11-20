# appointment_manager.py
# AppointmentManager holds the scheduling RULES:
#   - patient and clinician must exist
#   - date/time must be valid, in the future, and inside clinic hours
#   - a clinician cannot have two appointments at the same time (conflict)

from datetime import datetime
from clinic_app.decorators import log_action, time_it
from clinic_app.models import Appointment, check_date, check_time

OPEN_TIME = "08:00"
CLOSE_TIME = "17:00"
SLOT_MINUTES = 30  # every appointment lasts 30 minutes


def to_minutes(time_text):
    """'09:30' -> 570 (minutes since midnight). Makes time maths easy."""
    hours, minutes = time_text.split(":")
    return int(hours) * 60 + int(minutes)


def sort_key(appointment):
    return appointment.get_date() + " " + appointment.get_time()


class AppointmentManager:
    def __init__(self, patients, clinicians, appointments):
        self.patients = patients
        self.clinicians = clinicians
        self.appointments = appointments

    # ----- helpers -----
    def find_appointment(self, appt_id):
        for appt in self.appointments:
            if appt.get_id() == appt_id.strip().upper():
                return appt
        raise ValueError("Appointment " + appt_id + " does not exist.")

    def next_id(self):
        highest = 0
        for appt in self.appointments:
            number = int(appt.get_id()[1:])
            if number > highest:
                highest = number
        return "A" + str(highest + 1).zfill(3)

    def check_slot(self, date, time):
        """Checks the date and time are allowed. Returns cleaned (date, time)."""
        date = check_date(date)
        time = check_time(time)
        if date + " " + time <= datetime.now().strftime("%Y-%m-%d %H:%M"):
            raise ValueError("The appointment must be in the future.")
        if time < OPEN_TIME or to_minutes(time) + SLOT_MINUTES > to_minutes(CLOSE_TIME):
            raise ValueError("Clinic hours are " + OPEN_TIME + " to " + CLOSE_TIME +
                             " (last appointment starts 16:30).")
        return date, time

    def find_conflict(self, clinician_id, date, time, ignore_id=None):
        """Looks for an ACTIVE appointment for the same clinician that overlaps."""
        for appt in self.appointments:
            if appt.get_id() == ignore_id:
                continue
            if appt.get_clinician_id() != clinician_id:
                continue
            if appt.get_date() != date or not appt.is_active():
                continue
            gap = abs(to_minutes(appt.get_time()) - to_minutes(time))
            if gap < SLOT_MINUTES:  # starts less than 30 min apart = overlap
                return appt
        return None

    # ----- operations (the decorator logs each one) -----
    @log_action
    def schedule(self, patient_id, clinician_id, date, time, purpose):
        patient_id = patient_id.strip().upper()
        clinician_id = clinician_id.strip().upper()

        if patient_id not in [p.get_id() for p in self.patients]:
            raise ValueError("Patient " + patient_id + " does not exist.")
        if clinician_id not in [c.get_id() for c in self.clinicians]:
            raise ValueError("Clinician " + clinician_id + " does not exist.")

        date, time = self.check_slot(date, time)

        clash = self.find_conflict(clinician_id, date, time)
        if clash is not None:
            raise ValueError("Conflict! That clinician already has appointment " +
                             clash.get_id() + " at " + clash.get_time() + " on " +
                             clash.get_date() + ".")

        appointment = Appointment(self.next_id(), patient_id, clinician_id,
                                  date, time, purpose)
        self.appointments.append(appointment)
        return appointment

    @log_action
    def reschedule(self, appt_id, new_date, new_time):
        appointment = self.find_appointment(appt_id)
        if not appointment.is_active():
            raise ValueError("Only scheduled appointments can be rescheduled.")
        new_date, new_time = self.check_slot(new_date, new_time)
        clash = self.find_conflict(appointment.get_clinician_id(), new_date,
                                   new_time, ignore_id=appointment.get_id())
        if clash is not None:
            raise ValueError("Conflict! That clinician already has appointment " +
                             clash.get_id() + " at that time.")
        appointment.reschedule(new_date, new_time)
        return appointment

    @log_action
    def cancel(self, appt_id):
        appointment = self.find_appointment(appt_id)
        appointment.cancel()
        return appointment

    @log_action
    def complete(self, appt_id):
        appointment = self.find_appointment(appt_id)
        appointment.complete()
        return appointment

    # ----- reports -----
    def for_patient(self, patient_id):
        patient_id = patient_id.strip().upper()
        if patient_id not in [p.get_id() for p in self.patients]:
            raise ValueError("Patient " + patient_id + " does not exist.")
        found = [a for a in self.appointments if a.get_patient_id() == patient_id]
        return sorted(found, key=sort_key)

    def for_clinician(self, clinician_id):
        clinician_id = clinician_id.strip().upper()
        if clinician_id not in [c.get_id() for c in self.clinicians]:
            raise ValueError("Clinician " + clinician_id + " does not exist.")
        found = [a for a in self.appointments if a.get_clinician_id() == clinician_id]
        return sorted(found, key=sort_key)

    def for_date(self, date):
        date = check_date(date)
        found = [a for a in self.appointments if a.get_date() == date]
        return sorted(found, key=sort_key)

    @time_it
    def daily_summary(self, date):
        appts = self.for_date(date)
        scheduled = [a for a in appts if a.get_status() == "scheduled"]
        completed = [a for a in appts if a.get_status() == "completed"]
        cancelled = [a for a in appts if a.get_status() == "cancelled"]

        lines = ["===== Summary for " + check_date(date) + " =====",
                 "Total: " + str(len(appts)),
                 "Active (scheduled): " + str(len(scheduled)),
                 "Completed: " + str(len(completed)),
                 "Cancelled: " + str(len(cancelled))]
        for appt in appts:
            lines.append("  " + str(appt))
        return "\n".join(lines)
