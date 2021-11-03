# supermind
# Classic colour code-breaking game.
#
# Copyright (C) 2021 Jaime Alvarez Fernandez
# Contact: https://github.com/Jaime-alv
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
# ==========================================================================
import pathlib
import random
import string
import json
import re
import tkinter as tk
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
        self.profile = {}
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
        new_item.add_command(label='Profile statistics', command=self.show_profile)
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
        self.name_entry = tk.Entry(self.new_profile_window, textvariable=self.user_name)
        self.name_entry.pack()
        self.name_entry.focus()
        submit = tk.Button(self.new_profile_window, text='Submit', command=self.validate_name)
        submit.pack()

    def validate_name(self):
        user = self.user_name.get()
        self.create_profile_list()
        valid_characters = string.ascii_letters + string.digits + "_-."
        if all(c in valid_characters for c in user):
            self.player = user
            self.create_json()
        else:
            if user == '':
                messagebox.showerror('Error!', "Name can't be empty!")
            elif user in self.profile_list:
                messagebox.showerror('Error!', "There is another user with that name!")
            else:
                messagebox.showerror('Error!', "Please, only valid characters!")
            self.user_name.set('')
            self.name_entry.focus()

    def create_json(self):
        stat = {'wins': 0,
                'loses': 0,
                'fastest': 100}
        data = {'name': self.player,
                'config': {
                    'difficulty': '',
                    'colours': 0,
                    'holes': 0,
                    'total_rounds': 0,
                    'total_games': 0,
                    'extra_hard': False},
                'continue': {'bool': False,
                             'game_number': 0,
                             'current_game': {}},
                'statistics': {'easy': {},
                               'normal': {},
                               'hard': {},
                               'custom': {}}}
        for dif in data['statistics']:
            new_stats = dict(stat)
            # noinspection PyTypeChecker
            data['statistics'][dif] = new_stats
        if not pathlib.Path('profiles').exists():
            pathlib.Path('profiles').mkdir(exist_ok=True)
        save_profile(data, self.player)
        self.new_profile_window.destroy()

        # set player to new user and ask for a new game
        self.profile = read_profile(self.player)
        self.select_difficult()

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
        self.profile = read_profile(self.player)
        if self.profile['continue'].get('bool', None):
            message = 'There is a game going.\nWould you like to continue it?'
            if messagebox.askyesno('Continue', message=message):
                self.game_window()
            else:
                self.select_difficult()
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
            reset_continue_mode(self.profile, self.player)
            self.select_difficult_window = tk.Toplevel()
            self.select_difficult_window.title('Options')
            # divided in 2 frames; left for normal modes, right for custom
            left_frame = tk.Frame(self.select_difficult_window)
            left_frame.pack(side='left')
            choose_label = tk.Label(left_frame, text='Choose a difficulty')
            choose_label.pack()
            four_buttons = tk.Frame(left_frame)
            four_buttons.pack()
            # easy (6 colours, 3 holes)
            easy = tk.Button(four_buttons, text='Easy', command=self.easy)
            easy.grid(column=0, row=0)
            # normal (6 colours, 4 holes)
            normal = tk.Button(four_buttons, text='Normal', command=self.normal)
            normal.grid(column=0, row=1)
            # hard (8 colours, 5 holes)
            hard = tk.Button(four_buttons, text='Hard', command=self.hard)
            hard.grid(column=1, row=0)
            # custom (up to 8 colours, up to 8 holes?)
            custom = tk.Button(four_buttons, text='Custom', command=self.custom_frame)
            custom.grid(column=1, row=1)

            # radiobutton with classic mode and extra hard mode
            self.game_mode = tk.BooleanVar()
            classic_mode = tk.Radiobutton(left_frame, text='Classic mode', value=False, variable=self.game_mode,
                                          state='active')
            classic_mode.pack(anchor='w')
            extra_hard = tk.Radiobutton(left_frame, text='Extra hard mode', value=True, variable=self.game_mode)
            extra_hard.pack(anchor='w')

            # ask for number of total_games
            games_label = tk.Label(left_frame, text="How many total_games will be playing?")
            games_label.pack()
            self.games = tk.StringVar()
            self.games.set('3')
            entry = tk.Entry(left_frame, textvariable=self.games)
            entry.focus()
            self.terminate(left_frame, self.select_difficult_window, 'Close window')
            entry.pack(pady=5, padx=10, anchor='n', side='bottom', ipady=4)
        else:
            messagebox.showerror('Error!', 'Load a profile first!')

    # set options
    def difficulty(self, dif):
        games = self.games.get()
        if games.isdigit() and int(games) > 0:
            self.profile['config'] = dif
            self.profile['config']['extra_hard'] = self.game_mode.get()
            self.profile['config']['total_games'] = int(games)
            save_profile(self.profile, self.player)
            self.game_window()
        else:
            messagebox.showerror('Error!', 'Number of total_games should be higher than 0!')
            self.select_difficult()

    # easy
    def easy(self):
        self.difficulty({'difficulty': 'easy', 'colours': 6, 'holes': 3, 'total_rounds': 12})

    # normal
    def normal(self):
        self.difficulty({'difficulty': 'normal', 'colours': 6, 'holes': 4, 'total_rounds': 12})

    # hard
    def hard(self):
        self.difficulty({'difficulty': 'hard', 'colours': 8, 'holes': 5, 'total_rounds': 14})

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
        # how many total_rounds
        rounds_ask = tk.Label(questions_frame, text='How many total_rounds?')
        rounds_ask.grid(column=0, row=2)
        self.rounds = tk.IntVar()
        self.rounds.set(15)
        rounds_spin = tk.Spinbox(questions_frame, from_=1, to=50, width=3, textvariable=self.rounds)
        rounds_spin.grid(column=1, row=2)
        # submit button
        submit_button = tk.Button(right_frame, text='Submit', command=self.custom)
        submit_button.pack(side='bottom', anchor='s')

    # custom
    def custom(self):
        if (0 < self.colours.get() < 9) and (0 < self.holes.get() < 11) and (0 < self.rounds.get() < 51):
            colours = self.colours.get()
            holes = self.holes.get()
            rounds = self.rounds.get()
            self.difficulty({'difficulty': 'custom', 'colours': colours, 'holes': holes, 'total_rounds': rounds})
        else:
            messagebox.showerror('Error!', 'Please, enter valid inputs!')

    # show profile statistics
    def show_profile(self):
        if self.player != '':
            player_profile = read_profile(self.player)
            # create new window
            profile_window = tk.Toplevel()
            profile_window.title(self.player)
            self.terminate(profile_window, profile_window, 'Close')

            # statistics for easy difficulty
            easy_frame = tk.Frame(profile_window)
            easy_frame.pack(anchor='w')
            self.profile_unpack(easy_frame, player_profile['statistics']['easy'], 'Easy')

            # statistics for normal difficulty
            normal_frame = tk.Frame(profile_window)
            normal_frame.pack(anchor='w')
            self.profile_unpack(normal_frame, player_profile['statistics']['normal'], 'Normal')

            # statistics for hard difficulty
            hard_frame = tk.Frame(profile_window)
            hard_frame.pack(anchor='w')
            self.profile_unpack(hard_frame, player_profile['statistics']['hard'], 'Hard')

            # statistics for custom difficulty
            custom_frame = tk.Frame(profile_window)
            custom_frame.pack(anchor='w')
            self.profile_unpack(custom_frame, player_profile['statistics']['custom'], 'Custom')

        else:
            messagebox.showerror('Error!', 'Select a profile first!')

    # print profile function
    def profile_unpack(self, where, profile, dif):
        easy_label = tk.Label(where, text=f'» {dif}:')
        easy_label.grid(column=0, row=0, sticky='w')
        if profile.get('wins') + profile.get('loses') > 0:
            total_games = profile.get('wins') + profile.get('loses')
            total = tk.Label(where, text=f'    ·Total games: {total_games}')
            total.grid(column=0, row=1, sticky='w')
            win_games = profile.get('wins')
            win = tk.Label(where, text=f'    ·Total wins: {win_games}')
            win.grid(column=0, row=2, sticky='w')
            loss_games = profile.get('loses')
            loss = tk.Label(where, text=f'    ·Total loses: {loss_games}')
            loss.grid(column=0, row=3, sticky='w')
            win_loss_ratio = round(win_games * 100 / total_games, 2)
            win_loss = tk.Label(where, text=f'    ·Win/Loss ratio: {win_loss_ratio}%')
            win_loss.grid(column=0, row=4, sticky='w')
            fastet_game = profile.get('fastest')
            fastest = tk.Label(where, text=f'    ·Shortest game: {fastet_game} rounds')
            fastest.grid(column=0, row=5, sticky='w')
        else:
            nothing = tk.Label(where, text='    ·No data.')
            nothing.grid(column=0, row=1, sticky='w')

    # create game window
    def game_window(self):
        try:
            self.select_difficult_window.destroy()
        except AttributeError:
            pass
        GameWindow(self, self.player)
        self.withdraw()


class GameWindow(tk.Toplevel):
    def __init__(self, master, player):
        super().__init__()
        logging.debug(f'Start GameWindow with profile: {player}')
        self.player = player
        self.master = master
        self.title('Supermind')
        self.resizable(False, False)
        self.profile = read_profile(self.player)

        # unpack all fields
        self.holes = self.profile['config'].get('holes')
        self.total_rounds = self.profile['config'].get('total_rounds')
        self.total_games = self.profile['config'].get('total_games')
        self.difficulty = self.profile['config'].get('difficulty')
        self.extra_hard = self.profile['config'].get('extra_hard')

        self.player_choice = {}  # place for storing player choice until hit 'submit'
        self.available_colours = []  # available colours for the current game

        # check for saved game
        if not self.profile['continue'].get('bool'):
            self.current_game = {}  # dict for saving game state and all player choices
            self.secret_code = []  # secret color code player needs to guess
            self.round = 1  # Current round
            self.game_number = 1  # Current game
        else:
            self.current_game = self.profile['continue'].get('current_game')
            self.secret_code = self.profile['continue']['current_game']['pc']
            self.game_number = self.profile['continue'].get('game_number')
            self.round = len(self.profile['continue']['current_game']['player']) + 1

        self.set_up()
        if self.round >= self.total_rounds:
            self.after_game()
        self.main()

    # set up and configure total_games
    def set_up(self):
        rainbow_colour = ['red', 'blue', 'green', 'yellow', 'orange', 'indigo', 'violet', 'white']
        for n in range(self.profile['config'].get('colours')):
            self.available_colours.append(rainbow_colour[n])
        logging.debug(self.available_colours)
        # create dict with n colours for storing player choice
        for n in range(self.holes):
            self.player_choice.setdefault(n, '')
        logging.debug(self.player_choice)
        self.right_frame_window()
        self.left_frame_window()

    # round counter at left most side
    def column_round_counter(self):
        column_round = tk.Frame(self.frame_inside_canvas, bg='black')
        column_round.pack(side='left')
        for game_round in range(1, (self.total_rounds * 2) + 1):
            row = ((self.total_rounds * 2) + 1) - game_round
            if game_round % 2 != 0:
                rd_number = int((game_round / 2) + 1)
                round_number_text = tk.Label(column_round, text=f'{rd_number:02}', bg=board_colour)
                round_number_text.grid(column=0, row=row, pady=1, padx=1)
            else:
                result_round_text = tk.Label(column_round, text='00', fg=board_colour, bg=board_colour)
                result_round_text.grid(column=0, row=row, pady=1, padx=1)

    # main game loop
    def main(self):
        if self.game_number <= self.total_games:
            self.select_colours()
        else:
            # game is over, time to reset 'continue'
            reset_continue_mode(self.profile, self.player)
            messagebox.showinfo('Goodbye', 'Thank you!')
            self.close()

    # read number of colours game is going to use, and append to a list
    # randomize colours and get secret code
    def select_colours(self):
        while len(self.secret_code) < self.holes:
            colour = random.choice(self.available_colours)
            self.secret_code.append(colour)
        self.current_game.setdefault('pc', self.secret_code)  # save game estate
        self.current_game.setdefault('player', {})
        logging.critical(f'SECRET CODE = {self.secret_code}')

    # hide secret code
    def hide_secret(self):
        self.secret_frame = tk.Frame(self.top_frame, bg='black')
        self.secret_frame.pack(side='right')

        # print pc code
        for n in range(self.holes):
            label = tk.Label(self.secret_frame, text='', fg='black', bg='#2c2c30', width=11)
            label.grid(column=(n + 1), row=0, padx=1, pady=1)

    # uncover secret code frame
    def uncover_secret(self):
        self.submit_player['state'] = 'disabled'
        self.secret_frame.destroy()
        self.uncover_frame = tk.Frame(self.top_frame, bg='black')
        self.uncover_frame.pack(side='right')

        for n in range(len(self.secret_code)):
            label = tk.Label(self.uncover_frame, text='', fg='black', bg=self.secret_code[n], width=11)
            label.grid(column=(n + 1), row=0, padx=1, pady=1)

    def left_frame_window(self):
        show_scrollbar = False
        # board's left side (secret code, answer and game state)
        self.left_frame = tk.Frame(self)
        self.left_frame.pack(side='left', expand=1, fill='both')

        # secret code frame
        self.top_frame = tk.Frame(self.left_frame, bg='black')
        self.top_frame.pack(side='top', anchor='e', expand=1, fill='both')
        zero_secret = tk.Label(self.top_frame, text='00', fg='black', bg='black')
        zero_secret.pack(side='left')
        self.hide_secret()

        # get how much height canvas need
        total_height = self.get_total_height()
        self.unit.destroy()
        screen = self.winfo_screenheight()  # get screen height in pixel
        if total_height > int((screen * 3) / 4):
            show_scrollbar = True
            total_height = int((screen * 3) / 4)

        self.board_canvas = tk.Canvas(self.left_frame, bg=board_colour)
        self.top_frame.update()
        extension = self.top_frame.winfo_width()

        if show_scrollbar:
            self.board_canvas.configure(width=extension, height=total_height)
            self.board_canvas.update()
            self.board_canvas.pack(expand=0, fill='y')

            scrollbar = tk.Scrollbar(self, command=self.board_canvas.yview)
            scrollbar.pack(side='left', fill='y')
            self.board_canvas.configure(yscrollcommand=scrollbar.set)

            # update scrollregion after starting 'mainloop'
            # when all widgets are in canvas
            self.board_canvas.bind('<Configure>', self.on_configure)

        else:
            self.board_canvas.configure(width=(extension - 2), height=(total_height - 2))
            self.board_canvas.update()
            self.board_canvas.pack(expand=0, fill='y')

        self.frame_inside_canvas = tk.Frame(self.board_canvas, bg=board_colour)
        self.board_canvas.create_window((0, 0), window=self.frame_inside_canvas, anchor='nw')

        # total_rounds frame (center frame with all player solutions)
        self.column_round_counter()
        self.print_save_board()

        # answer frame
        player_frame = tk.Frame(self.left_frame, bg='black')
        player_frame.pack(side='bottom', anchor='s', expand=1, fill='both')
        zero_player = tk.Label(player_frame, text='00', fg='black', bg='black')
        zero_player.grid(column=0, row=0, padx=1)

        for n in range(self.holes):
            combo = ttk.Combobox(player_frame, width=10, values=self.available_colours, state="readonly")
            combo.grid(column=(n + 1), row=0, padx=1)
            combo.bind("<<ComboboxSelected>>", lambda event, i=n: self.choice_sel(event, i))

    # update scrollregion after starting 'mainloop'
    # when all widgets are in canvas
    def on_configure(self, event):
        self.board_canvas.configure(scrollregion=self.board_canvas.bbox('all'))

    def get_total_height(self):
        self.unit = tk.Frame(self.left_frame)
        self.unit.pack()
        for game_round in range(self.total_rounds * 2):
            row = tk.Label(self.unit)
            row.grid(column=0, row=game_round, pady=1)
        self.unit.update()
        return self.unit.winfo_height()

    def right_frame_window(self):
        # board's right side (buttons, round, game)
        self.right_frame = tk.Frame(self)
        self.right_frame.pack(side='right', expand=1, fill='both', ipadx=20)

        # game counter
        game_counter = tk.Frame(self.right_frame)
        game_counter.pack(anchor='center', expand=1)
        self.game_label = tk.Label(game_counter, text=f'Game #:{self.game_number}')
        self.game_label.pack(anchor='w', pady=5)

        # round counter
        round_counter = tk.Frame(self.right_frame)
        round_counter.pack(anchor='n', side='top', expand=0)
        self.round_label = tk.Label(round_counter, text=f'Round #:{self.round}')
        self.round_label.pack(anchor='w', pady=5)

        # submit button
        self.submit_player = tk.Button(self.right_frame, text="Submit", command=self.everything_ok)
        self.submit_player.pack(anchor='s', side='bottom', pady=2, ipadx=20)

        # close window & save game
        close = tk.Button(self.right_frame, text='Close & save', fg='red', command=self.close)
        close.pack(side='bottom', anchor='s', pady=2)

    # update game counter
    def update_game_counter(self):
        new_game = f'Game #:{self.game_number}'
        self.game_label.configure(text=new_game)

    # update round counter
    def update_round_counter(self):
        new_round = f'Round #:{self.round}'
        self.round_label.configure(text=new_round)

    # save player's choice in a dictionary so it can be checked later
    def choice_sel(self, event, i):
        self.player_choice[i] = event.widget.get()

    # form validation from submit button
    def everything_ok(self):
        if all(self.player_choice.get(c) != '' for c in self.player_choice):
            self.compare_player()
        else:
            messagebox.showerror('Error!', 'There is an empty field.')

    # compare player against secret code
    def compare_player(self):
        logging.info(f'Player choice in round {self.round} = {self.player_choice}')
        choice = {}  # Player choice in dict form for saving game estate
        for key in self.player_choice:
            choice.setdefault(str(key), self.player_choice.get(key))
        # now I need a list for counting items, if player puts 2 of the same colour and secret has only one, only one
        # peg in result should be displayed
        if self.extra_hard:
            results = self.extra_hard_mode()
        else:
            results = self.classic_mode()

        # save game state
        self.current_game['player'].setdefault(str(self.round), {})
        self.current_game['player'][str(self.round)].setdefault('choice', choice)
        self.current_game['player'][str(self.round)].setdefault('result', results)

        # add one more round to counter
        self.round += 1
        self.update_round_counter()
        self.center_frame.destroy()
        self.print_save_board()
        logging.warning(f'Result = {results}')
        logging.critical(self.current_game)

        # win or lose condition
        if all(results.get(c) == 'black' for c in results):
            self.uncover_secret()
            messagebox.showinfo('Congratulations!', 'You win.')
            self.profile['statistics'][self.difficulty]['wins'] += 1
            if self.profile['statistics'][self.difficulty].get('fastest') > (self.round - 1):
                self.profile['statistics'][self.difficulty]['fastest'] = (self.round - 1)
            self.after_game()

        elif self.round > self.total_rounds:
            self.uncover_secret()
            messagebox.showinfo('Sorry!', f"You lose. I was thinking in:\n{self.secret_code}")
            self.profile['statistics'][self.difficulty]['loses'] += 1
            self.after_game()

    # extra hard option
    def extra_hard_mode(self):
        results = {}
        for c in self.player_choice:
            if self.player_choice.get(c) == self.secret_code[int(c)]:
                results.setdefault(str(c), 'black')
            elif self.player_choice.get(c) in self.secret_code:
                results.setdefault(str(c), 'white')
            else:
                results.setdefault(str(c), None)
        return results

    # classic mode
    def classic_mode(self):
        secret = list(self.secret_code)  # Need a new list I can modify for already used colours.
        results = {}
        for c in self.player_choice:
            if self.player_choice.get(c) == secret[int(c)]:
                results.setdefault(str(c), 'black')
                secret[int(c)] = 'used'
            else:
                results.setdefault(str(c), 'wrong')
        for c in self.player_choice:
            if results.get(str(c)) == 'wrong':
                if self.player_choice.get(c) in secret:
                    results[str(c)] = 'white'
                    for x in range(len(secret)):
                        if self.player_choice.get(c) == secret[x]:
                            secret[x] = 'used'
                            break
                else:
                    results[str(c)] = None
        return results

    # after game, clean and reset fields, call main again
    def after_game(self):
        save_profile(self.profile, self.player)
        self.game_number += 1
        self.round = 1
        self.current_game.clear()  # clean game state
        self.secret_code.clear()  # clear secret in a new game round
        self.center_frame.destroy()
        self.print_save_board()
        # update game counter
        self.update_game_counter()
        # reset round counter to 1
        self.update_round_counter()
        self.uncover_frame.destroy()
        self.hide_secret()
        self.submit_player['state'] = 'normal'
        self.main()

    # print board and past choices, from bottom to top
    # uneven rows are player choices
    # even rows are the result from comparing player choices against the secret code
    def print_save_board(self):
        self.center_frame = tk.Frame(self.frame_inside_canvas, bg='black')
        self.center_frame.pack()
        for game_round in range(1, (self.total_rounds * 2) + 1):
            row = ((self.total_rounds * 2) + 1) - game_round
            if game_round % 2 != 0:  # player choice
                for peg in range(self.holes):
                    try:
                        tag_colour = self.current_game['player'][str((game_round // 2) + 1)]['choice'].get(str(peg), None)
                        # json file stores int as str
                    except KeyError:
                        tag_colour = None
                    if tag_colour is None:
                        tag_colour = board_colour
                    player_result = tk.Label(self.center_frame, bg=tag_colour, width=11)
                    player_result.grid(column=peg, row=row, padx=1, pady=1)
            elif game_round % 2 == 0:  # result
                for peg in range(self.holes):
                    try:
                        tag_colour = self.current_game['player'][str((game_round // 2))]['result'].get(str(peg), None)
                    except KeyError:
                        tag_colour = None
                    if tag_colour is None:
                        tag_colour = board_colour
                    player_result = tk.Label(self.center_frame, bg=tag_colour, width=11)
                    player_result.grid(column=peg, row=row, padx=1, pady=1)

    # close window and call MainWindow again
    def close(self):
        if self.round > 1 or 1 < self.game_number <= self.total_games:
            self.save_all()
        self.master.deiconify()
        self.destroy()

    # save game estate to profile file
    def save_all(self):
        self.profile['continue']['bool'] = True
        self.profile['continue']['game_number'] = self.game_number
        self.profile['continue']['current_game'] = self.current_game
        save_profile(self.profile, self.player)


def reset_continue_mode(profile, player):
    profile['continue']['bool'] = False
    profile['continue']['game_number'] = 1
    profile['continue']['current_game'].clear()
    save_profile(profile, player)


def save_profile(profile, player):
    with pathlib.Path(f'profiles\\{player}.txt').open('w') as overwrite:
        json.dump(profile, overwrite)


def read_profile(player):
    with pathlib.Path(f'profiles\\{player}.txt').open('r') as read:
        profile = json.load(read)
    return profile


if __name__ == '__main__':
    logging.basicConfig(filename='..\\tests\\log.txt', level=logging.DEBUG,
                        format='%(asctime)s - %(levelname)s - %(message)s')
    pathlib.Path('..\\tests\\log.txt').open('w')
    board_colour = '#6a6c75'  # color code for board
    MainWindow().mainloop()
    logging.debug('close program')
