
import random
import sys
from termcolor import colored


# GOT TO RUN IN VSC OR PYCHARM IDLE IS TRASH

def print_menu():
    print("Lets play Wordle: ")
    print("Type a 5 letter word and hit enter!\n")


def read_random_word():
    with open("python/wordle/words.txt") as f:
        words = f.read().splitlines()
        return random.choice(words).lower()


print_menu()
play_again = ""

while play_again != 'q'.lower():
    word = read_random_word()

    for attempt in range(1, 6):
        guess = input().lower()

        sys.stdout.write('\x1b[1a')
        sys.stdout.write('\x1b[2k')

        for i in range(min(len(guess), 5)):
            if guess[i] == word[i]:
                print(colored(guess[i], 'green'), end="")
            elif guess[i] in word:
                print(colored(guess[i], 'yellow'), end="")
            else:
                print(guess[i], end="")

        print()

        if guess == word:
            print(colored(f"You win! You got the wordle in {attempt} attempt/s", 'red'))
            break

    play_again = colored(input("The word was " + word + " Type q to exit. Press any button to start over."), 'red')
    print()
