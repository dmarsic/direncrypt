-- direncrypt - Sync contents between encrypted and decrypted directories
-- Copyright (C) 2015  Domagoj Marsic
-- Distributed under GPL v3, see LICENSE for details.

DROP TABLE IF EXISTS register;
CREATE TABLE register (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    unencrypted_file    TEXT,
    encrypted_file      TEXT,
    public_id           TEXT,
    timestamp           DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX IF NOT EXISTS register_u ON register(unencrypted_file);

DROP TABLE IF EXISTS parameters;
CREATE TABLE parameters (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    key                 TEXT,
    value               TEXT
);

INSERT INTO parameters (key, value) VALUES
    ('plaindir', '~/DropboxLocal'),
    ('securedir', '~/Dropbox/Enc'),
    ('public_id', NULL),
    ('gpg_keyring', 'pubring.kbx'),
    ('gpg_homedir', '~/.gnupg'),
    ('gpg_binary', 'gpg2');

DROP TABLE IF EXISTS state;
CREATE TABLE state (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    key                 TEXT,
    value               TEXT
);

INSERT INTO state (key, value) VALUES
    ('last_timestamp', NULL);
