# Copyright (C) 2021 Jaime Alvarez Fernandez

import random
import tkinter as tk


# white = right colour, bad position
# black = right colour, right position

class Game:
    def __init__(self):
        self.colours = ['red', 'blue', 'green', 'yellow', 'orange', 'indigo', 'violet', 'white']
        self.pc_code = []
        self.player_code = []
        self.result = []
        self.round = 1
        self.pc_choose_colours()
        self.main()

    # main loop
    def main(self):
        while True:
            print(self.round)
            self.player_turn()
            if self.player_code == self.pc_code:
                print(f'You win in {self.round} rounds!')
                break
            else:
                self.compare_result()

    # pc chooses colours and set up code
    def pc_choose_colours(self):
        while len(self.pc_code) < 5:
            colour = random.choice(self.colours)
            self.pc_code.append(colour)
        return self.pc_code

    # player input 5 colours and try to break it
    def player_turn(self):
        print(f'WARNING: {self.pc_code}')
        print(f'Choose from: {self.colours}')
        colour1 = input('1@: ')
        self.player_code.append(colour1)
        colour2 = input('2@: ')
        self.player_code.append(colour2)
        colour3 = input('3@: ')
        self.player_code.append(colour3)
        colour4 = input('4@: ')
        self.player_code.append(colour4)
        colour5 = input('5@: ')
        self.player_code.append(colour5)

    # compare self.player_code with self.pc_code
    def compare_result(self):
        for index in range(len(self.player_code)):
            if self.player_code[index] == self.pc_code[index]:
                self.result.append('black')
            elif (self.player_code[index] != self.pc_code[index]) and (self.player_code[index] in self.pc_code):
                self.result.append('white')
            else:
                self.result.append(None)
        print(self.result)
        self.player_code.clear()
        self.result.clear()
        self.round += 1


class GameWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.master.title('Mastermind')
        self.master.geometry('300x800')
        self.pack(expand=1, fill='both')


if __name__ == '__main__':
    window = tk.Tk()
    app = GameWindow(window)
    app.mainloop()

