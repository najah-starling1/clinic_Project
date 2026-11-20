# Clinic Appointment Management System (Python CLI)

A simple menu-driven program for a small clinic. Staff can manage patients and
clinicians, book appointments (with clash prevention) and view reports.
Everything is saved in JSON files.

## Requirements
Python 3.10 or newer. No extra packages needed.

## How to run
```
cd clinic_simple
python main.py
```
Run the tests: `python -m unittest discover -s tests`

## Features
- **Patients:** register (auto ID P001, P002...), view, search, update. Blocks bad input and duplicates.
- **Clinicians:** register (C001...), view, search by name or specialisation, update.
- **Appointments:** schedule (A001...), reschedule, cancel, mark completed.
  Status is `scheduled`, `completed` or `cancelled`.
- **Rules:** patient and clinician must exist; date is `YYYY-MM-DD`; time is `HH:MM`;
  must be in the future; clinic hours 08:00-17:00; each visit is 30 minutes;
  a clinician cannot have two active appointments that overlap.
- **Reports:** by patient, by clinician, by date, and a daily summary.
- **Saving:** `data/patients.json`, `data/clinicians.json`, `data/appointments.json`
  are saved after every change. Missing, empty or damaged files are handled.

## How to use
Start the program and type the number of a menu option. Try this to see
conflict prevention: Appointments -> Schedule -> `P004`, `C001`, `2026-12-01`, `09:15`.
(Sample appointments are in December 2026. If that date has passed, schedule
two appointments for the same clinician and time in the future instead.)

## Project structure
```
clinic_simple/
  main.py                       starts the program
  clinic_app/                   all the program code (a Python package)
    __init__.py
    cli.py                      menus (asks questions, prints answers)
    clinic.py                   Clinic: owns the lists, loads/saves, coordinates
    appointment_manager.py      scheduling rules, conflict detection, reports
    models.py                   Person, Patient, Clinician, Appointment
    storage.py                  JSONStorage: reads/writes JSON files
    decorators.py               log_action and time_it
  data/                         sample JSON files
  tests/test_clinic.py          simple tests
  logs/                         log file made when you run the program
```

## How to explain it (code defence)
- **Inheritance:** `Patient` and `Clinician` inherit from `Person` (name, phone, ID).
  Patient adds date of birth; Clinician adds specialisation.
- **Encapsulation:** attributes start with `__` so they are private. They are read
  with `get_...` methods and changed with `set_...` methods that check the value first.
  An appointment's status only changes through `cancel()`, `complete()`, `reschedule()`.
- **Relationships in JSON:** an appointment stores only `patient_id` and `clinician_id`.
  When loading, `Clinic.load_all()` checks those IDs exist and skips any that do not.
  It also skips duplicate IDs. If any records are skipped, the original file is first
  copied to `<file>.backup` so no data is lost when the program saves again.
- **Conflict detection:** `find_conflict()` looks for an active appointment with the same
  clinician, same date, and a start time less than 30 minutes away. Cancelled and
  completed appointments are ignored.
- **Decorators:** `@log_action` writes each schedule/reschedule/cancel/complete to
  `logs/clinic_log.txt`. `@time_it` shows how long the daily summary took.
- **Separation:** cli.py = screen, clinic.py = coordination, appointment_manager.py = rules,
  models.py = data objects, storage.py = files.
- **Error handling:** rules raise `ValueError` with a clear message; the menus catch it and print it.

## Git and project board
Use feature branches (e.g. `feature/patients`, `feature/appointments`, `feature/reports`)
with clear commit messages. Project board link: <add your Trello/Jira link here>
