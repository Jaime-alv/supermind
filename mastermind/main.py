# Copyright (C) 2021 Jaime Alvarez Fernandez
import pathlib
import random
import tkinter as tk
import json


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
        self.terminate()
        self.main_window()

    # close main window
    def terminate(self):
        close_program = tk.Button(self, fg='red', command=self.master.destroy)
        close_program['text'] = 'Close game'
        close_program['padx'] = 5
        close_program['pady'] = 5
        close_program.pack(side='bottom')

    # create main frame
    def main_window(self):
        new_profile = tk.Button(self, text='New profile', command=self.create_new_profile)
        new_profile.pack()
        self.user_name = tk.StringVar()
        name_entry = tk.Entry(self, textvariable=self.user_name)
        name_entry.pack()
        name_entry.focus()
        load_profile = tk.Button(self, text='Load profile', command=self.load_profile)
        load_profile.pack()

    # create a new profile
    def create_new_profile(self):
        user = self.user_name.get()
        with pathlib.Path(f'profiles\\{user}.txt').open('w') as file:
            json.dump({'name': user}, file)

    # load an existing profile
    def load_profile(self):
        for file in pathlib.Path('profiles\\').iterdir():
            print(file)


if __name__ == '__main__':
    window = tk.Tk()
    app = GameWindow(window)
    app.mainloop()
