PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE texts (
id integer not null primary key,
userid integer not null,
message text not null
);
COMMIT;
