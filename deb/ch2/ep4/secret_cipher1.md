# Data Security: Hashing and Encryption

As data engineers, you'll likely be working with data that needs to be kept secure, like credit card information. While the encryption exercises we're doing here are far from secure enough to use professionally, they're a good occasion to introduce the topic. 

Data is generally kept secure through either hashing or encryption. __Hashing__ takes an input value, passes it through a mathematical algorithm, and returns a hash value. The hashing algorithm is deterministic, meaning that the same inputted value will always get the same outputted value. Hashing is a one-way process: once plaintext is passed through a hash function, it can't be reversed. Hashing is often used to validate the authenticity of various kinds of input. For instance, the hashed values of passwords can be stored in databases, and compared to the hashed value of an inputted password; if they match, that password is correct. Storing passwords as hashes instead of as plaintext words keeps them private even if the database is compromised. Hashing is also used to prove that data hasn't been modified. For instance, Git uses hash functions to identify file changes. Hashing is in the background of much day-to-day security, like encrypting an email, sending a message on your phone, or connecting to an HTTPS website. It's also essential to cryptocurrency. 

Creating hash functions is an advanced topic, and usually left to the likes of the National Security Agency. Once a hash function is shown to be secure, it can become widely used. A common one, [SHA-256](https://en.wikipedia.org/wiki/SHA-2), is used for password hashing in Unix systems and by Bitcoin for verifying transactions. 

<br>

### Exercise
You can generate the SHA-256 hash for a file in the command line, using
```bash
sha256sum <FILENAME>
```
Get the SHA-256 hash for the `secret_message.txt` file. Run the same command again. What do you notice about the hashes? Now, change the contents of the file (just adding or deleting a letter is enough) and save it. Get the hash again. What happened this time?

Repeat the above steps, but this time try the MD5 hash:
```bash
md5sum <FILENAME>
```

<br>

__Encryption__, by contrast, has been designed and used by laypeople since ancient history, and is a reversible process. It allows someone to send a coded message that can (ideally) only be deciphered with a secret key. One of the most famous examples of the use of encryption and cryptanalysis in modern history is that of Alan Turing, a founder of computer science, who deciphered encrypted messages sent during World War II, helping the Allies to win the war. 

Commonly known ciphers used for encryption include the [Vigenere cipher](https://en.wikipedia.org/wiki/Vigenere_cipher), the [Caesar cipher](https://en.wikipedia.org/wiki/Caesar_cipher), and the [Affine cipher](https://en.wikipedia.org/wiki/Affine_cipher). The only truly secure type of cipher, still used in some contexts today despite its impracticality, is encrypting with a one-time pad. Here, we'll be trying the reverse cipher and the Caesar cipher. They're both quite easy to crack, but a good place to start.

# Secret Cipher 1: Reverse Cipher

This exercise will give us practice reading and writing to files, as well as creative problem solving with Python. There are just a few simple steps:

1. There's a file in this directory called 'secret_message.txt'. Feel free to change what the message is!

1. Open and read `secret_message.txt`.

1. Reverse the contents of `secret_message.txt`. 

1. Write the reversed contents to a new file.


There are a lot of ways to do this, so feel free to get creative.