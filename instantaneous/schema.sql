DROP TABLE IF EXISTS cardpool;

CREATE TABLE cardpool (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pool_id TEXT UNIQUE NOT NULL,
  data BLOB NOT NULL
);