import random

def rollDice():
    dice = [1, 2, 3, 4, 5, 6]
    random.shuffle(dice)
    return dice[0]

# Roll the die and print the result
result = rollDice()
print("You rolled:", result)
