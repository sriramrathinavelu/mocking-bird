CREATE KEYSPACE 
IF NOT EXISTS mockingbird 
WITH replication = {
	'class'					:	'SimpleStrategy',
	'replication_factor'	:	3
};

USE mockingbird;

/* Creation of Tables begin */

CREATE TABLE
IF NOT EXISTS users(
	userid					TIMEUUID,
	username				TEXT,
	firstname				TEXT,
	lastname				TEXT,
	email					TEXT,
	phone					TEXT,
	rating					INT,
	ctime					TIMESTAMP,
	mtime					TIMESTAMP,
	PRIMARY KEY (userid, rating)
)
WITH CLUSTERING ORDER BY (rating DESC);

CREATE TABLE
IF NOT EXISTS usertests(
	userid					TIMEUUID,
	totaltests				INT	STATIC,
	testid					TIMEUUID,
	username				TEXT,
	testname				TEXT,
	retrorating				INT,
	companyid				TIMEUUID,
	positionid				TIMEUUID,
	companyname				TEXT,
	positionname			TEXT,
	state					INT,			// 0 -> Not Begun, 1-> In Process , 2 -> Completed 
	totalquestions			INT,
	questionsanswered		INT,
	currentquestion			INT,
	isevaluated				BOOLEAN,
	totalmarks				FLOAT,
	scoredmarks				FLOAT,
	teststarttime			TIMESTAMP,
	testendtime				TIMESTAMP,
	userstarttime			TIMESTAMP,
	userendtime				TIMESTAMP,
	ctime					TIMESTAMP,
	mtime					TIMESTAMP,
	PRIMARY KEY (userid, testid)
) 
WITH CLUSTERING ORDER BY (testid DESC);


/*

For the below tables we prefer wide rows
over skinny rows
*/

CREATE TABLE
IF NOT EXISTS usercompany(
	userid					TIMEUUID,
	companyid				TIMEUUID,
	totaltests				INT,
	companyname				TEXT,
	PRIMARY KEY((userid, companyid))
);


CREATE TABLE
IF NOT EXISTS userposition(
	userid					TIMEUUID,
	positionid				TIMEUUID,
	totaltests				INT,
	positionname			TEXT,
	PRIMARY KEY ((userid, positionid))
);


CREATE TABLE 
IF NOT EXISTS companyposition(
	companyid				TIMEUUID,
	companyname				TEXT,
	totalpositions			INT,
	PRIMARY KEY (companyid)
);

CREATE TABLE 
IF NOT EXISTS positioncompany(
	positionid				TIMEUUID,
	positionname			TEXT,
	totalcompanies			INT,
	PRIMARY KEY (positionid)
);

CREATE TABLE 
IF NOT EXISTS positionrevlookup(
	positionname			TEXT,
	positionid				TIMEUUID,
	PRIMARY KEY (positionname)
);
