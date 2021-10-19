# Copyright (C) 2021 Jaime Alvarez Fernandez
import pathlib
import random
import tkinter as tk
import json
import re
from tkinter import messagebox


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
        self.profile_list = []
        self.for_delete = []
        self.master = master
        self.master.title('Mastermind')
        self.master.geometry('250x250')
        self.pack(expand=1, fill='both')
        self.terminate(self, self.master, 'Close game')
        self.main_window()

    # create profile_list
    def create_profile_list(self):
        self.profile_list.clear()
        for file in pathlib.Path('profiles').iterdir():
            file_str = str(file)
            name = re.compile(r'profiles\\(?P<name>.*?)\.txt')
            search = name.search(file_str)
            self.profile_list.append(search.group('name'))

    # close main window
    def terminate(self, where, what, text):
        close_program = tk.Button(where, fg='red', command=what.destroy, text=text)
        close_program['padx'] = 5
        close_program['pady'] = 5
        close_program.pack(side='bottom')

    # create main frame
    def main_window(self):
        new_profile = tk.Button(self, text='New profile', command=self.create_new_profile)
        new_profile.pack()
        load_profile = tk.Button(self, text='Load profile', command=self.load_profile)
        load_profile.pack()
        delete_profile = tk.Button(self, text='Delete profile', command=self.delete_profile)
        delete_profile.pack()

    # create a new profile
    def create_new_profile(self):
        self.new_profile_window = tk.Toplevel(self)
        self.new_profile_window.title('New profile')
        self.terminate(self.new_profile_window, self.new_profile_window, 'Close window')
        label = tk.Label(self.new_profile_window, text='Enter your name')
        label.pack()
        self.user_name = tk.StringVar()
        name_entry = tk.Entry(self.new_profile_window, textvariable=self.user_name)
        name_entry.pack()
        name_entry.focus()
        submit = tk.Button(self.new_profile_window, text='Submit', command=self.create_json)
        submit.pack()

    def create_json(self):
        user = self.user_name.get()
        if user != '':
            with pathlib.Path(f'profiles\\{user}.txt').open('w') as file:
                json.dump({'name': user}, file)
            self.new_profile_window.destroy()
        else:
            messagebox.showerror('Error!', "Name can't be empty!")


    # load an existing profile
    def load_profile(self):
        self.load_profile_window = tk.Toplevel(self)
        self.load_profile_window.title('Select a profile')
        self.terminate(self.load_profile_window, self.load_profile_window, 'Close window')
        self.create_profile_list()
        for index in range(len(self.profile_list)):
            button_with_name = tk.Button(self.load_profile_window, text=self.profile_list[index],
                                         command=lambda i=index: self.print_this(self.profile_list[i]))
            button_with_name.pack(anchor='w')

    def print_this(self, name):
        print(name)
        self.load_profile_window.destroy()

    # Delete an existing profile
    def delete_profile(self):
        self.delete_profile_window = tk.Toplevel(self)
        self.delete_profile_window.title('Delete profile')
        self.terminate(self.delete_profile_window, self.delete_profile_window, 'Close window')
        self.create_profile_list()
        for index in range(len(self.profile_list)):
            button_with_name = tk.Button(self.delete_profile_window, text=self.profile_list[index],
                                         command=lambda i=index: self.del_this(self.profile_list[i]))
            button_with_name.pack(anchor='w', padx=5, pady=5, ipady=5)

    def del_this(self, i):
        pathlib.Path.unlink(pathlib.Path(f'profiles\\{i}.txt'), missing_ok=True)
        self.delete_profile_window.destroy()
        self.delete_profile()


if __name__ == '__main__':
    window = tk.Tk()
    app = GameWindow(window)
    app.mainloop()
