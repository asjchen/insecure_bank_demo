DROP TABLE IF EXISTS BankAccount;

CREATE TABLE BankAccount(
	Username		VARCHAR(20) PRIMARY KEY,
	Salt			CHAR(8) NOT NULL,
	PasswordHash	CHAR(40) NOT NULL,
	Amount			MONEY
);
