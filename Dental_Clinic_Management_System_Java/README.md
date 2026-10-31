# Dental Clinic Management System
**College project:** Android Studio (Java + XML) + Flask REST API + shared SQLite + browser interface.

## Architecture
- Android app (Java/XML) and browser UI (HTML/CSS/JavaScript) call the same Flask API.
- SQLite database is stored on the computer/server running Flask. It is NOT a separate database file on each Android device.
- Dental images are stored in `backend/uploads`; metadata is in SQLite.
- Android emulator uses `http://10.0.2.2:5000/api/`. A physical phone and server PC must be on the same Wi-Fi and `ApiClient.java` must use the PC's LAN IP.

## Requirements
- Python 3.10+
- Android Studio with Android SDK (compile SDK 35)
- Internet is needed once to download Gradle dependencies.

## Start backend and web interface
Windows:
```bat
cd backend
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
set DENTAL_SECRET_KEY=replace-this-with-a-long-random-secret
python app.py
```
macOS/Linux:
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DENTAL_SECRET_KEY='replace-this-with-a-long-random-secret'
python app.py
```
Open `http://127.0.0.1:5000`. Demo login: `admin` / `ChangeMe123!`.
Change demo credentials and secret before any use beyond a classroom demo.

## Open Android project
1. In Android Studio choose **Open** and select the `android` directory.
2. Allow Gradle sync. Use JDK 17 if prompted.
3. Start an Android emulator, then Run.
4. The app is configured for emulator-to-host access via `10.0.2.2`.
5. For a physical Android device, change `BASE_URL` in `app/src/main/java/com/example/dentalclinic/ApiClient.java` to `http://YOUR_PC_LAN_IP:5000/api/`. Keep phone and PC on the same trusted Wi-Fi. Development HTTP is enabled only for local demo.

## Included modules
- Login and role field
- Patient registration and search
- Medical history
- Dental treatment categories: X-rays, implants, tooth extraction, caries filling, missing teeth, bridges, crowns, removable partial dentures (RPD), periodontitis treatment, scaling
- Dental image upload endpoint and browser upload UI
- Child dental chart for ages 6–12, stored in the patient's record
- Appointments and cancellation
- Follow-ups
- Upcoming reminder queue endpoint and browser view

## Reminder delivery
The project queues due reminders and shows upcoming reminders. Actual SMS/email sending needs an email/SMS provider account and configuration; it is intentionally not faked. Integrate a provider and protect API credentials if your course requires actual delivery.

## Security notes
This is an educational starter, not a clinically validated product. Use synthetic data only. Before any real patient data: deploy behind HTTPS, use a production WSGI server, replace the demo account and secret, enforce least-privilege roles, validate file uploads, add audit logs, backups/restore testing, consent and retention policies, and obtain professional privacy/security review. SQLite is suitable for a small demonstration, not high-concurrency clinical production.
