# Copyright (C) 2021 Jaime Alvarez Fernandez
import pathlib
import random
import tkinter as tk
import json
import re
from tkinter import messagebox
from tkinter import ttk
import logging


# white = right colour, bad position
# black = right colour, right position


class MainWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        logging.debug('Start main window')
        self.profile_list = []
        self.for_delete = []
        self.player = ''
        self.super_frame = tk.Frame(self)
        self.title('Supermind')
        self.geometry('250x250')
        self.super_frame.pack(expand=1, fill='both')
        self.terminate(self.super_frame, self, 'Close game')
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

    # close any window
    def terminate(self, where, what, text):
        close_program = tk.Button(where, fg='red', command=what.destroy, text=text)
        close_program['padx'] = 5
        close_program['pady'] = 5
        close_program.pack(side='bottom')

    # create menu
    def create_menu(self):
        logging.debug('print cascade menu')
        menu = tk.Menu(self.super_frame)

        new_item = tk.Menu(menu, tearoff=0)
        new_item.add_command(label='New profile', command=self.create_new_profile)
        new_item.add_command(label='Load profile', command=self.load_profile)
        new_item.add_command(label='Delete profile', command=self.delete_profile)
        new_item.add_separator()
        new_item.add_command(label='About')
        new_item.add_separator()
        new_item.add_command(label='Close', command=self.super_frame.destroy)

        menu.add_cascade(label='Options', menu=new_item)
        self.config(menu=menu)

    # create main frame
    def main_window(self):
        logging.debug('call main window')
        new_profile = tk.Button(self.super_frame, text='New profile', command=self.create_new_profile)
        new_profile.pack()
        load_profile = tk.Button(self.super_frame, text='Load profile', command=self.load_profile)
        load_profile.pack()
        delete_profile = tk.Button(self.super_frame, text='Delete profile', command=self.delete_profile)
        delete_profile.pack()
        play_game = tk.Button(self.super_frame, text='New game', command=self.select_difficult)
        play_game.pack()

    # create a new profile
    def create_new_profile(self):
        logging.debug('create new profile')
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
        data = {'name': user,
                'config': {
                    'difficulty': '',
                    'colours': 0,
                    'holes': 0,
                    'rounds': 0,
                    'games': 0},
                'continue': {'bool': False, 'game': {}},
                'easy': {},
                'normal': {},
                'hard': {},
                'custom': {}}
        if not pathlib.Path('profiles').exists():
            pathlib.Path('profiles').mkdir(exist_ok=True)
        if user != '':
            with pathlib.Path(f'profiles\\{user}.txt').open('w') as file:
                json.dump(data, file)
            self.new_profile_window.destroy()
        else:
            messagebox.showerror('Error!', "Name can't be empty!")

    # load an existing profile
    def load_profile(self):
        self.create_profile_list()
        if len(self.profile_list) != 0:
            self.load_profile_window = tk.Toplevel()
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
        if self.profile['continue'].get('bool', None):
            message = 'There is a game going.\nWould you like to continue it?'
            if messagebox.askyesno('Continue', message=message):
                self.game_window()
            else:
                self.select_difficult()
                self.profile['continue']['bool'] = False
                self.profile['continue']['game'].clear()
                with pathlib.Path(f'profiles\\{name}.txt').open('w') as overwrite:
                    json.dump(self.profile, overwrite)
            self.load_profile_window.destroy()
        else:
            self.select_difficult()
        self.load_profile_window.destroy()

    # Delete an existing profile
    def delete_profile(self):
        self.create_profile_list()
        if len(self.profile_list) > 0:
            self.delete_profile_window = tk.Toplevel()
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

    # select difficult panel
    def select_difficult(self):
        if self.player != '':
            self.select_difficult_window = tk.Toplevel()
            self.select_difficult_window.title('Choose your level')
            # divided in 2 frames; left for normal modes, right for custom
            left_frame = tk.Frame(self.select_difficult_window)
            left_frame.pack(side='left')
            four_buttons = tk.Frame(left_frame)
            four_buttons.pack()
            # easy (6 colours, 3 holes)
            easy = tk.Button(four_buttons, text='Easy', command=self.easy)
            easy.grid(column=0, row=0)
            # normal (6 colours, 4 holes)
            normal = tk.Button(four_buttons, text='normal', command=self.normal)
            normal.grid(column=0, row=1)
            # hard (8 colours, 5 holes)
            hard = tk.Button(four_buttons, text='Hard', command=self.hard)
            hard.grid(column=1, row=0)
            # custom (up to 8 colours, up to 8 holes?)
            custom = tk.Button(four_buttons, text='Custom', command=self.custom_frame)
            custom.grid(column=1, row=1)
            # ask for number of games
            games_label = tk.Label(left_frame, text="How many games will be playing?")
            games_label.pack()
            self.games = tk.StringVar()
            self.games.set('3')
            entry = tk.Entry(left_frame, textvariable=self.games)
            entry.focus()
            self.terminate(left_frame, self.select_difficult_window, 'Close window')
            entry.pack(pady=5, padx=10, anchor='n', side='bottom', ipady=4)
        else:
            messagebox.showerror('Error!', 'Load a profile first!')

    # check number of games is higher than 0
    def check_games(self):
        games = self.games.get()
        if games.isdigit() and int(games) > 0:
            return int(games)
        else:
            messagebox.showerror('Error!', 'Number of games should be higher than 0!')
            self.select_difficult()

    # easy
    def easy(self):
        games = self.check_games()
        self.profile['config']['difficulty'] = 'easy'
        self.profile['config']['colours'] = 6
        self.profile['config']['holes'] = 3
        self.profile['config']['rounds'] = 12
        self.profile['config']['games'] = games
        with pathlib.Path(f'profiles\\{self.player}.txt').open('w') as file:
            json.dump(self.profile, file)
        self.game_window()

    # normal
    def normal(self):
        games = self.check_games()
        self.profile['config']['difficulty'] = 'normal'
        self.profile['config']['colours'] = 6
        self.profile['config']['holes'] = 4
        self.profile['config']['rounds'] = 12
        self.profile['config']['games'] = games
        with pathlib.Path(f'profiles\\{self.player}.txt').open('w') as file:
            json.dump(self.profile, file)
        self.game_window()

    # hard
    def hard(self):
        games = self.check_games()
        self.profile['config']['difficulty'] = 'hard'
        self.profile['config']['colours'] = 8
        self.profile['config']['holes'] = 5
        self.profile['config']['rounds'] = 14
        self.profile['config']['games'] = games
        with pathlib.Path(f'profiles\\{self.player}.txt').open('w') as file:
            json.dump(self.profile, file)
        self.game_window()

    # custom mode (create new window for inputting values)
    def custom_frame(self):
        # append frame
        right_frame = tk.Frame(self.select_difficult_window)
        right_frame.pack(anchor='e', side='right')
        questions_frame = tk.Frame(right_frame)
        questions_frame.pack()
        # how many colours
        colours_ask = tk.Label(questions_frame, text='How many colours?')
        colours_ask.grid(column=0, row=0)
        self.colours = tk.IntVar()
        self.colours.set(5)
        colours_spin = tk.Spinbox(questions_frame, from_=1, to=8, width=3, textvariable=self.colours)
        colours_spin.grid(column=1, row=0)
        # how many holes
        holes_ask = tk.Label(questions_frame, text='How many holes?')
        holes_ask.grid(column=0, row=1)
        self.holes = tk.IntVar()
        self.holes.set(5)
        holes_spin = tk.Spinbox(questions_frame, from_=1, to=10, width=3, textvariable=self.holes)
        holes_spin.grid(column=1, row=1)
        # how many rounds
        rounds_ask = tk.Label(questions_frame, text='How many rounds?')
        rounds_ask.grid(column=0, row=2)
        self.rounds = tk.IntVar()
        self.rounds.set(20)
        rounds_spin = tk.Spinbox(questions_frame, from_=1, to=100, width=3, textvariable=self.rounds)
        rounds_spin.grid(column=1, row=2)
        # submit button
        submit_button = tk.Button(right_frame, text='Submit', command=self.custom)
        submit_button.pack(side='bottom', anchor='s')

    # custom
    def custom(self):
        games = self.check_games()
        if (0 < self.colours.get() < 9) and (0 < self.holes.get() < 11) and (0 < self.rounds.get() < 101):
            self.profile['config']['difficulty'] = 'custom'
            self.profile['config']['colours'] = self.colours.get()
            self.profile['config']['holes'] = self.holes.get()
            self.profile['config']['rounds'] = self.rounds.get()
            self.profile['config']['games'] = games
            with pathlib.Path(f'profiles\\{self.player}.txt').open('w') as file:
                json.dump(self.profile, file)
            self.game_window()
        else:
            messagebox.showerror('Error!', 'Please, enter valid inputs!')

    # create game window
    def game_window(self):
        self.select_difficult_window.destroy()
        GameWindow(self, self.player)
        self.withdraw()


class GameWindow(tk.Toplevel):
    def __init__(self, master, player):
        super().__init__()
        logging.debug(f'Start GameWindow with profile: {player}')
        self.master = master
        self.title('Supermind')
        self.big_frame = tk.Frame(self)
        self.big_frame.pack(expand=1, fill='both')
        with pathlib.Path(f'profiles\\{player}.txt').open('r') as read:
            self.profile = json.load(read)

        # unpack all fields
        self.holes = self.profile['config'].get('holes')
        self.rounds = self.profile['config'].get('rounds')
        self.games = self.profile['config'].get('games')
        self.dif = self.profile['config'].get('difficulty')

        self.game = {}  # dict for saving game state and all player choices
        self.colour_dict = {}  # place for storing player choice until hit 'submit'
        self.colours = []  # available colours for the current game
        self.secret = []  # secret color code player needs to get
        self.round = 1  # Current round
        self.game_number = 1  # Current game
        self.set_up()
        self.main()


    # set up and configure games
    def set_up(self):
        colour_list = ['red', 'blue', 'green', 'yellow', 'orange', 'indigo', 'violet', 'white']
        for n in range(self.profile['config'].get('colours')):
            self.colours.append(colour_list[n])
        logging.debug(self.colours)
        # create dict with n colours for storing player choice
        for n in range(self.holes):
            self.colour_dict.setdefault(n, '')
        logging.debug(self.colour_dict)
        self.right_frame_window()

    # main game loop
    def main(self):
        if self.game_number < (self.games + 1):
            self.select_colours()
            self.left_frame_window()
        else:
            messagebox.showinfo('Goodbye', 'Thank you!')
            self.close()

    # read number of colours game is going to use, and append to a list
    # randomize colours and get secret code
    def select_colours(self):
        while len(self.secret) < self.holes:
            colour = random.choice(self.colours)
            self.secret.append(colour)
        self.game.setdefault('pc', self.secret)  # save game estate
        self.game.setdefault('player', {})
        logging.critical(f'SECRET CODE = {self.secret}')

    def left_frame_window(self):
        # board's left side (secret code, answer and game state)
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side='left')

        # secret code frame
        secret_frame = tk.Frame(self.left_frame, bg=board_colour)
        secret_frame.pack(side='top', expand=1, fill='both')

        # print pc code
        for n in range(self.holes):
            label = tk.Label(secret_frame, text='', fg='black', bg=self.secret[n])
            label.grid(column=n, row=0, padx=1, pady=1, ipadx=38)

        # rounds frame (center frame with all player solutions)
        self.print_save_board()

        # answer frame
        player_frame = tk.Frame(self.left_frame, bg=board_colour)
        player_frame.pack(side='bottom', anchor='s', expand=1, fill='both')

        for n in range(self.holes):
            combo = ttk.Combobox(player_frame, width=10, values=self.colours, state="readonly")
            combo.grid(column=n, row=0, padx=1)
            combo.bind("<<ComboboxSelected>>", lambda event, i=n: self.choice_sel(event, i))

    def right_frame_window(self):
        # board's right side (buttons, round, game)
        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side='right')

        # game counter
        self.game_counter_call()

        # round counter
        self.round_counter_call()

        # submit button
        submit = tk.Button(self.right_frame, text="Submit", command=self.everything_ok)
        submit.pack(anchor='s', side='bottom')

        # close window & save game
        close = tk.Button(self.right_frame, text='Close', command=self.close)
        close.pack(side='bottom')

    # show game counter in right frame
    def game_counter_call(self):
        self.game_counter = tk.Frame(self.right_frame)
        self.game_counter.pack()
        game_label = tk.Label(self.game_counter, text=f'Game #:{self.game_number}')
        game_label.pack()

    # show round counter in right frame
    def round_counter_call(self):
        self.round_counter = tk.Frame(self.right_frame)
        self.round_counter.pack()
        round_label = tk.Label(self.round_counter, text=f'Round #:{self.round}')
        round_label.pack()

    # save player's choice in a dictionary so it can be checked later
    def choice_sel(self, event, i):
        self.colour_dict[i] = event.widget.get()

    # form validation from submit button
    def everything_ok(self):
        if all(self.colour_dict.get(c) != '' for c in self.colour_dict):
            self.compare_player()
        else:
            messagebox.showerror('Error!', 'There is an empty field.')

    # compare player against secret code
    def compare_player(self):
        logging.info(f'Player choice in round {self.round} = {self.colour_dict}')
        results = []  # Result from comparing player against secret code: black, white or None
        choice = dict(self.colour_dict)  # Player choice in dict form for saving game estate
        # now I need a list for counting items, if player puts 2 of the same colour and secret has only one, only one
        # peg in result should be displayed
        secret = list(self.secret)  # Need a new list I can modify for already used colours.
        results_dict = {}
        for c in self.colour_dict:
            if self.colour_dict.get(c) == secret[c]:
                results_dict.setdefault(c, 'black')
                results.append('black')
                secret[c] = 'used'
            elif self.colour_dict.get(c) != secret[c] and (self.colour_dict.get(c) in secret):
                value = 0
                for y in range(len(secret)):
                    if self.colour_dict.get(c) == secret[y]:
                        value = y
                        break
                secret[value] = 'used'
                results_dict.setdefault(c, 'white')
                results.append('white')
            else:
                results_dict.setdefault(c, None)
                results.append(None)

        # save game state
        self.game['player'].setdefault(self.round, {})
        self.game['player'][self.round].setdefault('choice', choice)
        self.game['player'][self.round].setdefault('result', results_dict)

        # add one more round to counter
        self.round += 1
        self.round_counter.destroy()
        self.round_counter_call()
        self.center_frame.destroy()
        self.print_save_board()
        logging.warning(f'Result = {results}')
        logging.critical(self.game)

        # win or lose condition
        if all(c == 'black' for c in results):
            messagebox.showinfo('Congratulations!', 'You win.')
            self.after_game()

        elif self.round > self.rounds:
            messagebox.showinfo('Sorry!', f"You lose. I was thinking in:\n{self.secret}")
            self.after_game()

    # after game, clean and reset fields, call main again
    def after_game(self):
        self.game_number += 1
        self.round = 1
        self.game.clear()  # clean game state
        self.secret.clear()  # clear secret in a new game round
        self.left_frame.destroy()
        self.game_counter.destroy()  # update game counter
        self.game_counter_call()
        self.round_counter.destroy()  # reset round counter to 1
        self.round_counter_call()
        self.main()

    # print board and past choices, from bottom to top
    # uneven rows are player choices
    # even rows are the result from comparing player choices against the secret code
    def print_save_board(self):
        self.center_frame = tk.Frame(self.left_frame, bg='black')
        self.center_frame.pack(side='top', anchor='n')
        for game_round in range(1, (self.rounds * 2) + 1):
            row = ((self.rounds * 2) + 1) - game_round
            if game_round % 2 != 0:
                for peg in range(self.holes):
                    try:
                        text = self.game['player'][(game_round // 2) + 1]['choice'].get(peg, None)
                    except KeyError:
                        text = None
                    if text is None:
                        text = board_colour
                    player_result = tk.Label(self.center_frame, bg=text)
                    player_result.grid(column=peg, row=row, padx=1, pady=1, ipadx=38)
            elif game_round % 2 == 0:
                for peg in range(self.holes):
                    try:
                        text = self.game['player'][(game_round // 2)]['result'].get(peg, None)
                    except KeyError:
                        text = None
                    if text is None:
                        text = board_colour
                    player_result = tk.Label(self.center_frame, bg=text)
                    player_result.grid(column=peg, row=row, padx=1, pady=1, ipadx=38)

    # close window and call MainWindow again
    def close(self):
        self.master.deiconify()
        self.destroy()


if __name__ == '__main__':
    logging.basicConfig(filename='..\\tests\\log.txt', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    pathlib.Path('..\\tests\\log.txt').open('w')
    board_colour = '#42413e'  # color code for board
    MainWindow().mainloop()
    logging.debug('close program')