# Simple tests. Run with:  python -m unittest discover -s tests
import os
import sys
import shutil
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from clinic_app.clinic import Clinic

SAMPLE_DATA = os.path.join(os.path.dirname(__file__), "..", "data")


class ClinicTests(unittest.TestCase):
    def setUp(self):
        # work on a copy so the real data files are never changed
        self.folder = tempfile.mkdtemp()
        for name in os.listdir(SAMPLE_DATA):
            shutil.copy(os.path.join(SAMPLE_DATA, name), self.folder)
        self.clinic = Clinic(self.folder)

    def tearDown(self):
        shutil.rmtree(self.folder, ignore_errors=True)

    def test_conflict_is_blocked(self):
        self.clinic.schedule("P001", "C001", "2030-01-07", "09:00", "First visit")
        with self.assertRaises(ValueError):
            self.clinic.schedule("P002", "C001", "2030-01-07", "09:15", "Clash")

    def test_back_to_back_is_allowed(self):
        self.clinic.schedule("P001", "C001", "2030-01-07", "09:00", "First visit")
        self.clinic.schedule("P002", "C001", "2030-01-07", "09:30", "Second visit")

    def test_cancelled_slot_can_be_reused(self):
        a = self.clinic.schedule("P001", "C001", "2030-01-07", "09:00", "First visit")
        self.clinic.cancel(a.get_id())
        self.clinic.schedule("P002", "C001", "2030-01-07", "09:00", "Reused slot")

    def test_bad_inputs(self):
        with self.assertRaises(ValueError):
            self.clinic.schedule("P999", "C001", "2030-01-07", "09:00", "No patient")
        with self.assertRaises(ValueError):
            self.clinic.schedule("P001", "C001", "2020-01-01", "09:00", "In the past")
        with self.assertRaises(ValueError):
            self.clinic.schedule("P001", "C001", "2030-01-07", "18:00", "After hours")
        with self.assertRaises(ValueError):
            self.clinic.schedule("P001", "C001", "not-a-date", "09:00", "Bad date")

    def test_reschedule_and_cancel(self):
        a = self.clinic.schedule("P001", "C001", "2030-01-07", "09:00", "First visit")
        self.clinic.reschedule(a.get_id(), "2030-01-08", "10:00")
        self.assertEqual(a.get_date(), "2030-01-08")
        self.clinic.cancel(a.get_id())
        self.assertEqual(a.get_status(), "cancelled")

    def test_data_is_saved(self):
        self.clinic.add_patient("Amina Yusuf", "+254700111222", "1990-04-04")
        new_clinic = Clinic(self.folder)
        self.assertEqual(len(new_clinic.patients), 7)

    def test_duplicate_patient(self):
        with self.assertRaises(ValueError):
            self.clinic.add_patient("anisa hassan", "+254700000000", "1994-03-12")

    def test_broken_json_files(self):
        with open(os.path.join(self.folder, "patients.json"), "w") as f:
            f.write("{ not valid json")
        open(os.path.join(self.folder, "appointments.json"), "w").close()
        new_clinic = Clinic(self.folder)
        self.assertEqual(len(new_clinic.patients), 0)
        self.assertEqual(len(new_clinic.appointments), 0)

    def test_duplicate_ids_in_file_are_skipped(self):
        with open(os.path.join(self.folder, "patients.json"), "w") as f:
            f.write('[{"id": "P001", "name": "Anisa Hassan", "phone": "+254712345601", "date_of_birth": "1994-03-12"},'
                    '{"id": "P001", "name": "Zamzam Abdi", "phone": "+254712345602", "date_of_birth": "1988-07-25"}]')
        new_clinic = Clinic(self.folder)
        self.assertEqual(len(new_clinic.patients), 1)

    def test_backup_made_when_records_are_skipped(self):
        # patients file is damaged -> appointments lose their patients
        with open(os.path.join(self.folder, "patients.json"), "w") as f:
            f.write("{ broken")
        Clinic(self.folder)
        self.assertTrue(os.path.exists(os.path.join(self.folder, "appointments.json.backup")))


if __name__ == "__main__":
    unittest.main()
