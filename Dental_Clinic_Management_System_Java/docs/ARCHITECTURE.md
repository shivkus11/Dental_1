# Architecture diagram

```mermaid
flowchart TD
  A[Android App<br/>Java + XML] -->|HTTP JSON| C[Flask REST API]
  B[Web Browser<br/>HTML CSS JavaScript] -->|HTTP JSON| C
  C --> D[(SQLite file on backend computer)]
  C --> E[Dental image uploads folder]
  C --> F[Reminder queue endpoint]
```

## ER diagram

```mermaid
erDiagram
  USERS ||--o{ PATIENTS : manages
  PATIENTS ||--|| MEDICAL_HISTORY : has
  PATIENTS ||--o{ TREATMENTS : receives
  PATIENTS ||--o{ DENTAL_CHARTS : has
  PATIENTS ||--o{ DENTAL_IMAGES : owns
  PATIENTS ||--o{ APPOINTMENTS : books
  PATIENTS ||--o{ FOLLOWUPS : needs
  TREATMENTS o|--o{ FOLLOWUPS : tracks
```

## Data flow
1. User signs in through Android or web browser.
2. Client sends authenticated requests to Flask.
3. Flask validates input and performs parameterized SQLite queries.
4. Patient image bytes are saved under `backend/uploads`; metadata is linked to patient in SQLite.
5. Both clients retrieve the same patient and appointment records from the server.
