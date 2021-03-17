DROP TABLE IF EXISTS device;

CREATE TABLE device(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tagGlobal TEXT UNIQUE NOT NULL,
    device_name TEXT NOT NULL,
    device_description TEXT
);
