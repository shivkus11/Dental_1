# Dental Clinic Management System — Project Report

## Abstract
The Dental Clinic Management System is an educational application that digitizes dental clinic workflows. It provides an Android app developed in Java and XML, a browser interface, a Flask REST API and a shared SQLite database hosted on the backend computer. The system manages patient profiles, medical histories, dental treatment records, dental images, child dental charts, appointments, reminders and follow-ups.

## Problem statement
Paper records can be hard to search, duplicate and keep current. A shared digital system helps authorized clinic users retrieve patient records and track care more consistently.

## Objectives
- Create digital patient profiles with unique patient codes.
- Record conditions, allergies, medications and previous surgeries.
- Maintain all requested dental treatment categories.
- Store before-and-after dental images and X-rays.
- Save a dedicated child dental chart for ages 6–12.
- Manage appointments and follow-up visits.
- Search patient records from Android and a browser.
- Demonstrate authentication, validation and centralized storage.

## Modules
1. Authentication.
2. Patient registration and search.
3. Medical history.
4. Dental treatments: X-rays, implants, tooth extraction, caries filling, missing teeth, bridges, crowns, RPD, periodontitis treatment and scaling.
5. Dental image upload and retrieval.
6. Child dental chart snapshots.
7. Appointment management and reminder queue.
8. Follow-up tracking.
9. Dashboard.

## Architecture
Android and web clients send JSON requests to the Flask API. The backend validates requests and stores data in a shared SQLite database. Image files are stored on the server and indexed in SQLite.

## Database design
The database includes users, patients, medical_history, treatments, dental_charts, dental_images, appointments and followups. Foreign keys connect patient-related records to their patient profile.

## Security
Passwords are hashed with PBKDF2-HMAC-SHA256. API endpoints require a session login. Queries use parameters. This is only a demonstration implementation; production deployment needs HTTPS, a production server, stronger role permissions, audit logging, secure backups, file-content validation and a formal privacy review.

## Limitations and future scope
Actual SMS/email delivery requires a configured provider. The chart stores tooth-status JSON rather than a fully interactive odontogram. Additional improvements include a visual tooth chart, role-based permissions, exportable reports, reminder delivery logs, encrypted backups and deployment behind HTTPS.

## Conclusion
The project demonstrates how an Android Java app and browser interface can access a common SQLite-backed service through a REST API. It is suitable as a starting point for a college project and requires further testing and security work before clinical use.
