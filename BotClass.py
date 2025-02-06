import random

# bot and letter classes written for a game of Wordle

class Letter:
    # initialize Letter class with instance variables
    # receives a single letter and its game relavant info from game engine
    def __init__(self, letter:str) -> None:
        self.letter = letter    
        self.in_correct_place: bool = False
        self.in_word:bool = False

    def is_in_correct_place(self) -> bool:
        return self.in_correct_place

    def is_in_word(self) -> bool:
        return self.in_word

class Bot:
    # initialize the bot with instance variables
    # receives a file object containing words for the game to load into a list
    def __init__(self, word_list_file:str) -> None:
        self.word_list:list[str] = []               # the list of word to make guesses from
        with open(word_list_file, 'r') as file:     # read the list of words from relevant file and load them into a list
            self.word_list = [line.strip().upper() for line in file.readlines()]
        self.known_pos:list[object] = [None]*5      # known letters and their positions for a given secret word
        self.misplaced:dict[str,int] = {}           # misplaced letters in the secret word
        self.invalid:set[str] = set()               # invalid letters in the secret word
        self.dictChoices:dict[str,int] = {}         # dictionary of available words based on score

    # the core algorithm to make guesses for the game engine
    def make_guess(self) -> str:            
        if any(self.known_pos):
            for word in self.word_list:
                if not word in self.dictChoices:
                    self.dictChoices.update({word:0})   # if the word isn't in the dict of choices, add it
                for i, letter in enumerate(word):
                    if letter == self.known_pos[i]: 
                        self.dictChoices[word] +=1      # for each letter in every word corresponding to a known letter,
                                                        # add one point to that word
            choices = list(sorted(self.dictChoices, reverse=True, key=self.dictChoices.get))    
            # create the list of available words to choose from based on their score
            choices_filtered = [key for key in choices if all(char not in key for char in self.invalid) and
                                all(char == self.known_pos[i] for i, char in enumerate(key) if self.known_pos[i] is not None)]
            # filter the list of choices: no invalid characters and the word must match all known positions
            if choices_filtered:
                guess = choices_filtered[0]             # next guess is the first element in the list of filtered choices
            else:
                choices = [choice for choice in self.word_list if all(char not in choice for char in self.invalid)]
                guess = random.choice(choices)          # if the list of filtered choices is empty, filter the word list for invalid letters and make a random guess
        elif any(self.misplaced):
            choices = [choice for choice in self.word_list if all(char not in choice for char in self.invalid) and 
                        all(char in choice for char in self.misplaced)]
            guess = random.choice(choices)
        else:
            choices = [choice for choice in self.word_list if all(char not in choice for char in self.invalid)]
            guess = random.choice(choices)
        self.word_list.remove(guess)
        return guess

    def record_guess_results(self, guess:str, guess_results:list[Letter]) -> None:
        for i, letter in enumerate(guess_results):
            char = guess[i]
            if letter.is_in_correct_place():
                self.known_pos[i] = char
            elif (not letter.is_in_correct_place()) and letter.is_in_word() and (letter not in self.misplaced.keys()):
                self.misplaced.update({char:i})
            elif not (letter.is_in_correct_place()) and (not letter.is_in_word()) and (letter not in self.invalid):
                self.invalid.add(char)