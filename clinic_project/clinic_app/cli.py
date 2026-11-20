# cli.py
# The menus. This file only asks questions and prints answers.
# All the rules live in the other files. If a rule is broken, the other files
# raise a ValueError and we print its message.

from clinic_app.clinic import Clinic


def show_list(items):
    if len(items) == 0:
        print("  Nothing found.")
    for item in items:
        print("  " + str(item))


def ask(question):
    return input(question + ": ").strip()


class ClinicCLI:
    def __init__(self):
        self.clinic = Clinic()

    # ---------- patient menu ----------
    def patient_menu(self):
        while True:
            print("\n--- PATIENTS ---")
            print("1. Register patient")
            print("2. View all patients")
            print("3. Search patients")
            print("4. Update patient")
            print("0. Back")
            choice = ask("Choose")
            if choice == "0":
                break
            try:
                if choice == "1":
                    p = self.clinic.add_patient(ask("Full name"), ask("Phone"),
                                                ask("Date of birth (YYYY-MM-DD)"))
                    print("Registered: " + str(p))
                elif choice == "2":
                    show_list(self.clinic.patients)
                elif choice == "3":
                    show_list(self.clinic.search_patients(ask("Name or ID to search")))
                elif choice == "4":
                    patient_id = ask("Patient ID")
                    print("Current: " + str(self.clinic.find_patient(patient_id)))
                    print("(Press Enter to keep the old value)")
                    p = self.clinic.update_patient(patient_id, ask("New name"),
                                                   ask("New phone"), ask("New date of birth"))
                    print("Updated: " + str(p))
                else:
                    print("Please choose a number from the menu.")
            except ValueError as error:
                print("Error: " + str(error))

    # ---------- clinician menu ----------
    def clinician_menu(self):
        while True:
            print("\n--- CLINICIANS ---")
            print("1. Register clinician")
            print("2. View all clinicians")
            print("3. Search (name or specialisation)")
            print("4. Update clinician")
            print("0. Back")
            choice = ask("Choose")
            if choice == "0":
                break
            try:
                if choice == "1":
                    c = self.clinic.add_clinician(ask("Full name"), ask("Phone"),
                                                  ask("Specialisation"))
                    print("Registered: " + str(c))
                elif choice == "2":
                    show_list(self.clinic.clinicians)
                elif choice == "3":
                    show_list(self.clinic.search_clinicians(ask("Search")))
                elif choice == "4":
                    clinician_id = ask("Clinician ID")
                    print("Current: " + str(self.clinic.find_clinician(clinician_id)))
                    print("(Press Enter to keep the old value)")
                    c = self.clinic.update_clinician(clinician_id, ask("New name"),
                                                     ask("New phone"), ask("New specialisation"))
                    print("Updated: " + str(c))
                else:
                    print("Please choose a number from the menu.")
            except ValueError as error:
                print("Error: " + str(error))

    # ---------- appointment menu ----------
    def appointment_menu(self):
        while True:
            print("\n--- APPOINTMENTS ---")
            print("1. Schedule appointment")
            print("2. Reschedule appointment")
            print("3. Cancel appointment")
            print("4. Mark appointment completed")
            print("0. Back")
            choice = ask("Choose")
            if choice == "0":
                break
            try:
                if choice == "1":
                    a = self.clinic.schedule(ask("Patient ID"), ask("Clinician ID"),
                                             ask("Date (YYYY-MM-DD)"), ask("Time (HH:MM)"),
                                             ask("Purpose"))
                    print("Scheduled: " + str(a))
                elif choice == "2":
                    a = self.clinic.reschedule(ask("Appointment ID"), ask("New date (YYYY-MM-DD)"),
                                               ask("New time (HH:MM)"))
                    print("Rescheduled: " + str(a))
                elif choice == "3":
                    print("Cancelled: " + str(self.clinic.cancel(ask("Appointment ID"))))
                elif choice == "4":
                    print("Completed: " + str(self.clinic.complete(ask("Appointment ID"))))
                else:
                    print("Please choose a number from the menu.")
            except ValueError as error:
                print("Error: " + str(error))

    # ---------- reports menu ----------
    def report_menu(self):
        manager = self.clinic.manager
        while True:
            print("\n--- REPORTS ---")
            print("1. Appointments for a patient")
            print("2. A clinician's schedule")
            print("3. Appointments on a date")
            print("4. Daily summary")
            print("0. Back")
            choice = ask("Choose")
            if choice == "0":
                break
            try:
                if choice == "1":
                    show_list(manager.for_patient(ask("Patient ID")))
                elif choice == "2":
                    show_list(manager.for_clinician(ask("Clinician ID")))
                elif choice == "3":
                    show_list(manager.for_date(ask("Date (YYYY-MM-DD)")))
                elif choice == "4":
                    print(manager.daily_summary(ask("Date (YYYY-MM-DD)")))
                else:
                    print("Please choose a number from the menu.")
            except ValueError as error:
                print("Error: " + str(error))

    # ---------- main menu ----------
    def run(self):
        print("===== CLINIC APPOINTMENT SYSTEM =====")
        for warning in self.clinic.warnings:
            print("[Warning] " + warning)

        while True:
            print("\n--- MAIN MENU ---")
            print("1. Patients")
            print("2. Clinicians")
            print("3. Appointments")
            print("4. Reports")
            print("0. Exit")
            try:
                choice = ask("Choose")
            except (EOFError, KeyboardInterrupt):
                break
            if choice == "1":
                self.patient_menu()
            elif choice == "2":
                self.clinician_menu()
            elif choice == "3":
                self.appointment_menu()
            elif choice == "4":
                self.report_menu()
            elif choice == "0":
                break
            else:
                print("Please choose a number from the menu.")

        self.clinic.save_all()
        print("\nData saved. Goodbye!")
