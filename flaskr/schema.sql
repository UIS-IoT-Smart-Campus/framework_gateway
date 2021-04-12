DROP TABLE IF EXISTS device;
DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS device_to_device;
DROP TABLE IF EXISTS property;

CREATE TABLE user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
);

CREATE TABLE device(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    tagGlobal TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    device_type TEXT NOT NULL,
    description TEXT
);

CREATE TABLE device_to_device(
    id_device_father INTEGER NOT NULL,
    id_device_son INTEGER NOT NULL,
    FOREIGN KEY (id_device_father) REFERENCES device(id), 
    FOREIGN KEY (id_device_son) REFERENCES device(id), 
    UNIQUE (id_device_father, id_device_son)
);

CREATE TABLE property(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    value TEXT NOT NULL,
    description TEXT,
    device_id INTEGER NOT NULL,    
    FOREIGN KEY (device_id) REFERENCES device(id)
);


