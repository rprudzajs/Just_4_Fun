import random

print("Your Password:  ")
characters = 'qwertyuiopasdfghjklzxcvbnm1234567890'
password = ''
for x in range(16):
    password += random.choice(characters)

print(password)

