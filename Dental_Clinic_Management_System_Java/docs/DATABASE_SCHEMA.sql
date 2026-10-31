CREATE TABLE users(id INTEGER PRIMARY KEY, username TEXT UNIQUE NOT NULL, password_hash TEXT NOT NULL, role TEXT NOT NULL);
CREATE TABLE patients(id INTEGER PRIMARY KEY, patient_code TEXT UNIQUE NOT NULL, full_name TEXT NOT NULL, dob TEXT, gender TEXT, phone TEXT, email TEXT, address TEXT, emergency_contact TEXT);
CREATE TABLE medical_history(id INTEGER PRIMARY KEY, patient_id INTEGER UNIQUE REFERENCES patients(id), conditions TEXT, allergies TEXT, medications TEXT, surgeries TEXT, notes TEXT);
CREATE TABLE treatments(id INTEGER PRIMARY KEY, patient_id INTEGER REFERENCES patients(id), category TEXT, tooth_number TEXT, treatment_date TEXT, description TEXT, cost REAL, status TEXT);
CREATE TABLE dental_charts(id INTEGER PRIMARY KEY, patient_id INTEGER REFERENCES patients(id), chart_type TEXT, chart_date TEXT, tooth_status_json TEXT, notes TEXT);
CREATE TABLE dental_images(id INTEGER PRIMARY KEY, patient_id INTEGER REFERENCES patients(id), filename TEXT, original_name TEXT, category TEXT, caption TEXT);
CREATE TABLE appointments(id INTEGER PRIMARY KEY, patient_id INTEGER REFERENCES patients(id), appointment_at TEXT, reason TEXT, doctor TEXT, status TEXT, reminder_sent INTEGER);
CREATE TABLE followups(id INTEGER PRIMARY KEY, patient_id INTEGER REFERENCES patients(id), treatment_id INTEGER REFERENCES treatments(id), due_date TEXT, notes TEXT, status TEXT);
