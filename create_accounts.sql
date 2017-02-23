DROP TABLE IF EXISTS BankAccount;

-- Note: the web.py interface does not allow casting to binary types 
-- when inserting rows (with db.insert) to my knowledge
CREATE TABLE BankAccount(
	Username		VARCHAR(20) PRIMARY KEY,
	Salt			CHAR(8) NOT NULL,
	PasswordHash	CHAR(40) NOT NULL,
	Amount			MONEY
);
INSERT INTO BankAccount VALUES('admin', '*Utf&+s5', 
	'317fe16a5f409e871b21c3460a75dab8dc906767', 0);
