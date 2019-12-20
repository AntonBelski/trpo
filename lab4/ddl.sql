CREATE TABLE User (
	Id SERIAL PRIMARY KEY,
	Name char (32) NOT NULL,
	Password char (16) NOT NULL,
	Level integer REFERENCES Level(Id),
	Role integer REFERENCES Role(Id)
);

CREATE TABLE Role (
	Id SERIAL PRIMARY KEY,
	Name char (32) NOT NULL
);

CREATE TABLE Level (
	Id SERIAL PRIMARY KEY,
	Experience_required integer NOT NULL
);

CREATE TABLE Task (
	Id SERIAL PRIMARY KEY,
	Name char (32) NOT NULL,
	Description char (256),
	Experience_award integer NOT NULL,
	Level_required integer REFERENCES Level(Id),
	Solution char(64) NOT NULL,
	Creator integer REFERENCES User(Id) NOT NULL
);

CREATE TABLE Article (
	Id SERIAL PRIMARY KEY,
	Name char(32) NOT NULL,
	Content char(512) NOT NULL,
	Author integer REFERENCES User(Id) NOT NULL
);

CREATE TABLE Task_status (
	User integer REFERENCES User(Id),
	Task integer REFERENCES Task(Id),
	Status char(32) NOT NULL,
	Attempts integer NOT NULL,
	PRIMARY KEY (User, Task)
);

CREATE TABLE Task_log (
	User integer REFERENCES User(Id),
	Task integer REFERENCES Task(Id),
	Name char(32) NOT NULL,
	Description char (256),
	Solution char (64) NOT NULL,
	Date date NOT NULL,
	PRIMARY KEY (User, Task)
);

CREATE TABLE Article_log (
	User integer REFERENCES User(Id),
	Article integer REFERENCES Article(Id),
	Name char(32) NOT NULL,
	Content char(512) NOT NULL,
	Date date NOT NULL,
	PRIMARY KEY (User, Article)
);