CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    branch TEXT NOT NULL,
    cgpa REAL NOT NULL,
    graduation_year INTEGER NOT NULL,
    backlogs INTEGER NOT NULL
);


CREATE TABLE placement_drives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    company TEXT NOT NULL,
    role TEXT NOT NULL,
    min_cgpa REAL NOT NULL,
    branches TEXT NOT NULL,
    graduation_year INTEGER NOT NULL,
    backlogs_allowed INTEGER NOT NULL
);


CREATE TABLE applications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    drive_id INTEGER NOT NULL,
    status TEXT NOT NULL DEFAULT 'Applied',

    FOREIGN KEY (student_id)
        REFERENCES students(id),

    FOREIGN KEY (drive_id)
        REFERENCES placement_drives(id),

    UNIQUE(student_id, drive_id)
);