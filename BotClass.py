from PIL import Image, ImageFont, ImageDraw
import random

# letter class made for a game of wordle for a coursera course
class Letter:
    def __init__(self, letter:str) -> None:
        self.letter = letter.upper()    
        self.in_correct_place: bool = False
        self.in_word:bool = False

    def is_in_correct_place(self) -> bool:
        return self.in_correct_place

    def is_in_word(self) -> bool:
        return self.in_word

# bot class v1 - made for a game of wordle in a Coursera course
class Bot:
    def __init__(self, word_list_file:str) -> None:
        self.word_list:list[str] = []               
        with open(word_list_file, 'r') as file:     
            self.word_list = [line.strip().upper() for line in file.readlines()]
        self.known_pos:list[object] = [None]*5      
        self.misplaced:dict[str,int] = {}           
        self.invalid:set[str] = set()               
        self.dictChoices:dict[str,int] = {}         

    def make_guess(self) -> str:            
        if any(self.known_pos):
            for word in self.word_list:
                if not word in self.dictChoices:
                    self.dictChoices.update({word:0})   
                for i, letter in enumerate(word):
                    if letter == self.known_pos[i]: 
                        self.dictChoices[word] +=1      
            choices = list(sorted(self.dictChoices, reverse=True, key=self.dictChoices.get))    
            choices_filtered = [key for key in choices if all(char not in key for char in self.invalid) and
                                all(char == self.known_pos[i] for i, char in enumerate(key) if self.known_pos[i] is not None)]
            
            if choices_filtered:
                guess = choices_filtered[0]             
            else:
                choices = [choice for choice in self.word_list if all(char not in choice for char in self.invalid)]
                guess = random.choice(choices)          
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

# data class for image info - made by coursera course faculty; included due to dependency in bot class below
class DisplaySpecification:
    """A dataclass for holding display specifications for WordyPy. The following
    values are defined:
        - block_width: the width of each character in pixels
        - block_height: the height of each character in pixels
        - correct_location_color: the hex code to color the block when it is correct
        - incorrect_location_color: the hex code to color the block when it is in the wrong location but exists in the string
        - incorrect_color: the hex code to color the block when it is not in the string
        - space_between_letters: the amount of padding to put between characters, in pixels
        - word_color: the hex code of the background color of the string
    """

    block_width: int = 80
    block_height: int = 80
    correct_location_color: str = "#00274C"
    incorrect_location_color: str = "#FFCB05"
    incorrect_color: str = "#D3D3D3"
    space_between_letters: int = 5
    word_color: str = "#FFFFFF"

# bot class v2 - made for a game of wordle for a coursera course; 
# this version makes guesses based on images
# dependent on the DisplaySpec class defined above
class Bot:
    def __init__(self, word_list_file:str, display_spec:DisplaySpecification) -> None:
        self.displaySpec = display_spec
        self.word_list:list[str] = []               
        with open(word_list_file, 'r') as file:     
            self.word_list = [line.strip().upper() for line in file.readlines()]
        self.known_pos:list[object] = [None]*5      
        self.misplaced:dict[str,int] = {}           
        self.invalid:set[str] = set()               
        self.dictChoices:dict[str,int] = {}

    def _tuple_to_str(self, pixels:str) -> str:
        pixelRedux:tuple = tuple([item for i, item in enumerate(pixels) if i != 3])
        webHex:str = bytearray(pixelRedux).hex()
        webHexCode:str = f'#{str(webHex).upper()}'
        return webHexCode

    def _process_image(self,guess:str, guess_image:Image.Image) -> list[Letter]:
        listLetters:list[Letter] = [] 
        x = self.displaySpec.block_width/2
        y = self.displaySpec.block_height/4
        
        for letter in guess:
            pixels = guess_image.getpixel((x,y))
            webHexCode = self._tuple_to_str(pixels)
            if webHexCode == self.displaySpec.correct_location_color:
                clsLetter = Letter(letter)
                clsLetter.in_correct_place = True
                listLetters.append(clsLetter)
            elif  webHexCode == self.displaySpec.incorrect_location_color:
                clsLetter = Letter(letter)
                clsLetter.in_word = True
                listLetters.append(clsLetter)
            elif webHexCode == self.displaySpec.incorrect_color:
                clsLetter = Letter(letter)
                listLetters.append(clsLetter)
            x += self.displaySpec.block_width
        return listLetters

    def make_guess(self) -> str:
        if not any(self.known_pos):
            guess = random.choice(self.word_list)
            
        elif any(self.misplaced):
            choices = [choice for choice in self.word_list if all(char not in choice for char in self.invalid) and 
                        all(char in choice for char in self.misplaced)]
            if choices:
                guess = random.choice(choices)
            else:
                guess = random.choice(self.word_list)
        
        elif any(self.known_pos):
                for word in self.word_list:
                    if not word in self.dictChoices:
                        self.dictChoices.update({word:0})   
                    for i, letter in enumerate(word):
                        if letter == self.known_pos[i]: 
                            self.dictChoices[word] +=1
                                                        
                choices = list(sorted(self.dictChoices, reverse=True, key=self.dictChoices.get))
                choices_filtered = [key for key in choices if all(char not in key for char in self.invalid) and
                                all(char == self.known_pos[i] for i, char in enumerate(key) if self.known_pos[i] is not None)]

                if choices_filtered:
                    guess = choices_filtered[0]             
                else:
                    choices = [choice for choice in self.word_list if all(char not in choice for char in self.invalid)]
                    if choices:
                        guess = random.choice(choices)
                    else:
                        guess = random.choice(self.word_list)
                
        self.word_list.remove(guess)
        return guess

    def record_guess_results(self, guess:str, guess_results:Image.Image) -> None:
        listLetters:list[Letter] = self._process_image(guess, guess_results)
        
        for i, letter in enumerate(listLetters):
            char = guess[i]
            if letter.is_in_correct_place():
                self.known_pos[i] = char
            elif (not letter.is_in_correct_place()) and letter.is_in_word() and (letter not in self.misplaced.keys()):
                self.misplaced.update({char:i})
            elif not (letter.is_in_correct_place()) and (not letter.is_in_word()) and (letter not in self.invalid):
                self.invalid.add(char)