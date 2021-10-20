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


class MainWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.profile_list = []
        self.for_delete = []
        self.player = ''
        self.master = master
        self.master.title('Mastermind')
        self.master.geometry('250x250')
        self.pack(expand=1, fill='both')
        self.terminate(self, self.master, 'Close game')
        self.main_window()
        self.create_menu()

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

    # create menu
    def create_menu(self):
        menu = tk.Menu(self.master)

        new_item = tk.Menu(menu, tearoff=0)
        new_item.add_command(label='New profile', command=self.create_new_profile)
        new_item.add_command(label='Load profile', command=self.load_profile)
        new_item.add_command(label='Delete profile', command=self.delete_profile)
        new_item.add_separator()
        new_item.add_command(label='About')
        new_item.add_separator()
        new_item.add_command(label='Close', command=self.master.destroy)

        menu.add_cascade(label='Options', menu=new_item)
        self.master.config(menu=menu)

    # create main frame
    def main_window(self):
        new_profile = tk.Button(self, text='New profile', command=self.create_new_profile)
        new_profile.pack()
        load_profile = tk.Button(self, text='Load profile', command=self.load_profile)
        load_profile.pack()
        delete_profile = tk.Button(self, text='Delete profile', command=self.delete_profile)
        delete_profile.pack()
        play_game = tk.Button(self, text='New game', command=self.select_difficult)
        play_game.pack()

    # create a new profile
    def create_new_profile(self):
        self.new_profile_window = tk.Toplevel(self)
        self.new_profile_window.title('New profile')
        self.terminate(self.new_profile_window, self.new_profile_window, 'Close window')
        label = tk.Label(self.new_profile_window, text='Enter your name:')
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
                json.dump({'name': user, 'continue': True}, file)
            self.new_profile_window.destroy()
        else:
            messagebox.showerror('Error!', "Name can't be empty!")

    # load an existing profile
    def load_profile(self):
        self.create_profile_list()
        if len(self.profile_list) != 0:
            self.load_profile_window = tk.Toplevel(self)
            self.load_profile_window.title('Select a profile')
            self.terminate(self.load_profile_window, self.load_profile_window, 'Close window')
            for index in range(len(self.profile_list)):
                button_with_name = tk.Button(self.load_profile_window, text=self.profile_list[index],
                                             command=lambda i=index: self.load_this(self.profile_list[i]))
                button_with_name.pack(anchor='w')
        else:
            messagebox.showerror('Error!', 'Create a profile first.')
            self.create_new_profile()

    def load_this(self, name):
        self.player = name
        with pathlib.Path(f'profiles\\{name}.txt').open('r') as file:
            self.profile = json.load(file)
        if self.profile.get('continue', None):
            message = 'There is a game going.\nWould you like to continue it?'
            if messagebox.askyesno('Continue', message=message):
                self.load_game()
            else:
                self.select_difficult()
                self.profile['continue'] = False
                with pathlib.Path(f'profiles\\{name}.txt').open('w') as overwrite:
                    json.dump(self.profile, overwrite)
            self.load_profile_window.destroy()
        else:
            self.select_difficult()
        self.load_profile_window.destroy()

    def load_game(self):
        print('Continue')

    # Delete an existing profile
    def delete_profile(self):
        self.create_profile_list()
        if len(self.profile_list) > 0:
            self.delete_profile_window = tk.Toplevel(self)
            self.delete_profile_window.title('Delete profile')
            self.terminate(self.delete_profile_window, self.delete_profile_window, 'Close window')
            for index in range(len(self.profile_list)):
                button_with_name = tk.Button(self.delete_profile_window, text=self.profile_list[index],
                                             command=lambda i=index: self.del_this(self.profile_list[i]))
                button_with_name.pack(anchor='w', padx=5, pady=5, ipady=5)
        else:
            messagebox.showerror('Error!', 'There are no profiles.\nCreate a new profile first.')
            self.create_new_profile()

    def del_this(self, i):
        pathlib.Path.unlink(pathlib.Path(f'profiles\\{i}.txt'), missing_ok=True)
        self.delete_profile_window.destroy()
        self.delete_profile()

    # select difficult panel
    def select_difficult(self):
        if self.player != '':
            self.select_difficult_window = tk.Toplevel(self)
            self.select_difficult_window.title('Choose your level')
            self.select_frame = tk.Frame(self.select_difficult_window)
            self.select_frame.pack()
            # easy (6 colours, 3 holes)
            easy = tk.Button(self.select_frame, text='Easy')
            easy.grid(column=0, row=0)
            # medium (6 colours, 4 holes)
            medium = tk.Button(self.select_frame, text='Medium')
            medium.grid(column=0, row=1)
            # hard (8 colours, 5 holes)
            hard = tk.Button(self.select_frame, text='Hard')
            hard.grid(column=1, row=0)
            # custom (up to 8 colours, up to 8 holes?)
            custom = tk.Button(self.select_frame, text='Custom')
            custom.grid(column=1, row=1)
            # ask for number of games
            games_label = tk.Label(text="How many games will be playing?")
            self.games = tk.IntVar()
            self.games.set(3)
            entry = tk.Entry(self.select_difficult_window, textvariable=self.games)
            entry.focus()
            self.terminate(self.select_difficult_window, self.select_difficult_window, 'Close window')
            entry.pack(pady=5, padx=10, anchor='n', side='bottom', ipady=4)
        else:
            messagebox.showerror('Error!', 'Load a profile first!')

    # easy
    def easy(self):
        print('Hi')

    # create game window
    def game_window(self):
        game_window = tk.Tk()
        game_window.title('Megamind')
        GameWindow(game_window)
        self.master.destroy()


class GameWindow(tk.Frame):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.pack(expand=1, fill='both')
        label = tk.Label(self, text='Hello')
        label.pack()
        close = tk.Button(self, text='Close', command=self.close)
        close.pack()

    def close(self):
        self.master.destroy()
        recall_window = tk.Tk()
        MainWindow(recall_window)


if __name__ == '__main__':
    window = tk.Tk()
    app = MainWindow(window)
    app.mainloop()
