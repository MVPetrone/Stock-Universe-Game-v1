import sys
import tkinter.ttk
from tkinter import *
from tkinter.font import Font
import pygame
import random
import time
import sqlite3
from PIL import ImageTk, Image
from database import Database
from datasheet import Datasheet
from login import Login


class Player:

    def __init__(self, username="Dev", player_key=None, dev_key=False):

        database.connect(path="./databases/logins.db")

        self.username = username
        self.player_key = player_key

        self.showing = False

        if dev_key:

            self.xp = 0
            self.xp_level = 0
            self.levels_unlocked = 1
            self.products_unlocked = 1
            self.balance = 5000
            self.capacity = 200

        else:

            database.cur.execute("SELECT * FROM PlayerData")
            info = database.cur.fetchall()[player_key]
            self.xp = info[1]
            self.xp_level = info[2]
            self.levels_unlocked = info[3]
            self.products_unlocked = info[4]
            self.balance = info[5]
            self.capacity = info[6]


class Level:

    def __init__(self, level_id, level_diff, line_delay, lines_amount, len_range, colour="black",
                 lines_array=None, profit_goal=None):  # make an object that has the basics to create a level
        database.create_origin_table()
        database.create_gem_table()
        database.create_decay_table()

        # Load Textures ================================================================================================

        self.power_img = ImageTk.PhotoImage(Image.open("./resources/textures/power.png"))
        self.play_img = ImageTk.PhotoImage(Image.open("./resources/textures/play.png"))
        self.pause_img = ImageTk.PhotoImage(Image.open("./resources/textures/pause.png"))
        self.restart_img = ImageTk.PhotoImage(Image.open("./resources/textures/restart.png"))
        self.speaker_img = ImageTk.PhotoImage(Image.open("./resources/textures/speaker.png"))
        self.speaker_muted_img = ImageTk.PhotoImage(Image.open("./resources/textures/speaker_muted.png"))
        self.level1_img = ImageTk.PhotoImage(Image.open("./resources/thumbnails/level1.png"))
        self.level2_img = ImageTk.PhotoImage(Image.open("./resources/thumbnails/level2.png"))
        self.wood_img = ImageTk.PhotoImage(Image.open("./resources/textures/product_wood.png"))
        self.lock_img = ImageTk.PhotoImage(Image.open("./resources/textures/lock.png"))

        # Load Sounds ==================================================================================================

        pygame.mixer.music.load("./resources/sound/music.wav")
        pygame.mixer.music.set_volume(0.06)
        pygame.mixer.music.play(-1)

        self.wood_sfx = pygame.mixer.Sound("./resources/sound/wood.wav")
        self.wood_sfx.set_volume(0.7)

        # Fonts ========================================================================================================

        self.times_font = Font(family="Times", size="10", weight="bold")
        self.button_font = Font(family="Times", size="8", weight="bold")
        self.button_font_underlined = Font(family="Times", size="8", weight="bold", underline=1)
        self.event_font = Font(family="Times", size="13", weight="bold")
        self.price_font = Font(family="David", size="20", weight="bold")
        self.stats_font = Font(family="David", size="9")
        self.transaction_font = Font(family="David", size="8")
        self.end_screen_title_font = Font(family="OCR", size="24", weight="bold")

        # ==============================================================================================================

        self.running = False
        self.level_id = level_id  # this is the primary key for each level layout that does not change
        self.level_diff = level_diff  # level difficulty
        self.line_delay = line_delay  # the time it takes for each line to spawn
        self.lines_amount = lines_amount  # the amount of lines
        if lines_array is None: lines_array = []
        self.lines_array = lines_array  # lines layout in object form
        self.lines_array_raw = []  # raw numbers and values in an array of tuples
        self.slideshow = False  # boolean to represent graph moving to the left
        self.graph_boundary = 800  # pixels from left to right  on the graph until slideshow starts
        self.transactions = []  # a list that stores the history of transactions that have been made during the level
        self.level_balance = player.balance  # the balance of the player in the level start
        self.transactions.append(self.level_balance)  # starting transaction is always what you start with
        self.profit = 0
        self.y_pos = 0
        self.x_pos = 0
        self.buy_count = 0
        self.sell_count = 0
        self.stocks_count = 0
        self.colour = colour
        self.len_range = len_range
        self.mouse_pos = []
        self.all_events = []
        self.level_events = []
        self.current_event_loading = None
        self.current_event = None
        self.showing_p_info = False
        self.showing_trans_log = False
        self.showing_levels_info = False
        self.buy_line = 700
        self.stock_mult_state = 1
        self.muted_music = False
        self.slideshow_trig = False
        self.won = False
        self.profit_goal = profit_goal

        # Widgets ======================================================================================================

        # Main Level Frame
        self.level_frame = Frame(root, relief=FLAT, cursor="circle", bd=0)
        self.level_frame.place(x=0, y=0)

        # Background canvas
        self.bg = Canvas(self.level_frame, bg="grey10", width=1300,
                         height=700, bd=0)
        self.bg.grid(row=0, column=0)

        # Datasheet
        self.datasheet = Datasheet(root, tkinter.ttk)

        # Graph frame at x=350, y=20
        self.graph_frame = Frame(self.level_frame, cursor="plus", bd=0)
        self.graph_frame.place(x=300, y=20, height=450, width=880)

        # Graph canvas
        self.graph_canvas = Canvas(self.graph_frame, bg="grey69", bd=0)
        self.graph_canvas.place(x=0, y=0, height=450, width=880)

        # Key binds
        root.bind("<Key>", self.keyboard_pressed)
        self.level_frame.bind("<Button-1>", self.mouse_pressed)

        # Buy Frame
        self.buy_frame = Frame(self.level_frame, bd=0)
        self.buy_frame.place(x=260 + 128 + 30 + 200, y=490 + 40, height=90, width=90)

        # Sell Frame
        self.sell_frame = Frame(self.level_frame, bd=0)
        self.sell_frame.place(x=260 + 128 + 30 + 200 + 90 + 10, y=490 + 40, height=90, width=90)

        # Buy Button
        self.buy_button = Button(self.buy_frame, bd=0, bg="lawn green", text="BUY\n\nZ", font=self.times_font,
                                 command=lambda: self.buy(), activebackground="lawn green")
        self.buy_button.place(x=0, y=0, height=90, width=90)

        # Sell Button
        self.sell_button = Button(self.sell_frame, bd=0, bg="lawn green", text="SELL\n\nX", font=self.times_font,
                                  command=lambda: self.sell(), activebackground="lawn green")
        self.sell_button.place(x=0, y=0, height=90, width=90)

        # Restart Button
        self.restart_button = Button(self.level_frame, bd=0, bg="lawn green", text="START\nR", font=self.times_font,
                                     command=lambda: self.start(), activebackground="lawn green")
        # self.restart_button.config(image=self.restart_img)
        self.restart_button.place(x=1100, y=480, height=40, width=64)

        # Quit Button
        self.quit = Button(self.level_frame, bd=0, text="QUIT", fg="lawn green", bg="grey10",
                           command=lambda: quit_())
        # self.quit.config(image=self.power_img)
        self.quit.place(x=1160, y=670)

        # Timer elapsed Label
        self.timer_label = Label(self.graph_frame, bg="grey69", text="0 seconds")
        self.timer_label.place(x=10, y=10, height=32, width=64)
        self.timer_label.destroy()

        # Balance Label
        self.update_balance = lambda x: "Balance\n£{}".format(x)
        self.level_balance_label = Label(self.level_frame, bg="grey10", fg="light blue", font=self.stats_font)
        self.level_balance_label.config(text=self.update_balance(self.level_balance))
        self.level_balance_label.place(x=260 + 128 + 30 + 185, y=480, height=30, width=60)

        # Profit label
        self.profit_label = Label(self.level_frame, font=self.stats_font)
        self.profit_label.config(text="Profit\n{}{}/{}".format("", 0, self.profit_goal), fg="green2", bg="grey10")
        self.profit_label.place(x=260 + 40 + 300 + 70, y=480, height=30, width=65)

        # Stocks Amount label
        self.update_stock = lambda x: "Stocks\n{}/{}".format(x, player.capacity)
        self.stocks_label = Label(self.level_frame, bg="grey10", fg="light blue", font=self.stats_font)
        self.stocks_label.config(text=self.update_stock(self.stocks_count))
        self.stocks_label.place(x=260 + 128 + 30 + 200 + 120, y=480, height=30, width=50)

        # Current Event Textbox
        self.event_textbox_frame = Frame(self.level_frame)
        self.event_textbox_frame.place(x=260 + 40, y=480, width=300, height=140)
        self.event_textbox = Text(self.event_textbox_frame, state=DISABLED, padx=50, pady=50, wrap=WORD,
                                  font=self.event_font)
        self.event_textbox.place(x=0, y=0, width=300, height=170)

        # Transaction Log Button
        self.trans_log_button = Button(self.level_frame, text="Transaction\nLog",
                                       command=lambda: self.change_tab('trans_log'), bd=0, bg="grey36", fg="light blue",
                                       font=self.button_font, activebackground="grey36", activeforeground="light blue")
        self.trans_log_button.place(x=5, y=20, height=60, width=63)

        # Transaction Log Listbox
        self.trans_log_listbox = Listbox(self.level_frame, bd=0, bg="grey36", fg="light blue", font=self.transaction_font)

        # Player Info Button
        self.p_info_button = Button(self.level_frame, text="Profile",
                                    command=lambda: self.change_tab('p_info'), bd=0, bg="SteelBlue2",
                                    font=self.button_font, activebackground="SteelBlue2")
        self.p_info_button.place(x=5, y=20+70, height=60, width=63)

        # Player Stat Labels
        self.p_info_frame = Frame(self.level_frame, bg="SteelBlue2", bd=1)

        self.p_info_username = Label(self.p_info_frame, text="{}'s stats".format(player.username), bg="SteelBlue2")
        self.p_info_username.place(x=4, y=5)

        self.p_info_xp = Label(self.p_info_frame, text="XP : {}".format(player.xp), bg="SteelBlue3")
        self.p_info_xp.place(x=4, y=5 + 35)

        self.p_info_xp_level = Label(self.p_info_frame, text="XP Level : {}".format(player.xp_level), bg="SteelBlue3")
        self.p_info_xp_level.place(x=4, y=5 + 35 + 30)

        self.p_info_balance = Label(self.p_info_frame, text="Balance : £{}".format(player.balance), bg="SteelBlue3")
        self.p_info_balance.place(x=4, y=5 + 35 + 30 + 30)

        self.p_info_capacity = Label(self.p_info_frame, text="Stock Capacity : {}".format(player.capacity), bg="SteelBlue3")
        self.p_info_capacity.place(x=4, y=5 + 35 + 30 + 30 + 30)

        # Levels Info Button
        self.levels_info_button = Button(self.level_frame, text="Levels",
                                         command=lambda: self.change_tab('levels_info'), bd=0, bg="cornsilk2",
                                         fg="RoyalBlue4", font=self.button_font, activebackground="cornsilk2",
                                         activeforeground="RoyalBlue4")
        self.levels_info_button.place(x=5, y=20 + 70 + 70, height=60, width=63)

        # Levels List Frames
        self.levels_info_frame = Frame(self.level_frame, bd=0, bg="cornsilk2")
        self.show_levels_info(True)

        self.level1_frame = Frame(self.levels_info_frame, bd=1, bg="black", cursor="hand2")
        self.level1_frame.place(x=5, y=5, height=50, width=56)

        self.level2_frame = Frame(self.levels_info_frame, bd=1, bg="black", cursor="hand2")
        self.level2_frame.place(x=5 + 60, y=5, height=50, width=56)

        # Levels List Image Labels
        self.level1_label = Label(self.level1_frame)
        self.level1_label.config(image=self.level1_img)
        self.level1_label.pack()

        self.level2_label = Label(self.level2_frame)
        self.level2_label.config(image=self.level2_img)
        self.level2_label.pack()

        # Levels List Text Labels
        self.level1_label = Label(self.level1_frame)
        self.level1_label.config(text="Level 1")
        self.level1_label.pack()

        self.level2_label = Label(self.level2_frame)
        self.level2_label.config(text="Level 2")
        self.level2_label.pack()

        # Level Stat Labels
        self.level1_product_label = Label(self.levels_info_frame, text="Level 1\nProduct: Wood", font=self.price_font,
                                          anchor=W, bg="cornsilk2", fg="RoyalBlue4")
        self.level1_product_label.place(x=10, y=75)

        self.level1_product_image = Label(self.levels_info_frame, image=self.wood_img, bg="cornsilk2")
        self.level1_product_image.place(x=25, y=170)

        self.level1_start_price_label = Label(self.levels_info_frame, text="Stock Price: £{}".format(225),
                                              anchor=W, bg="cornsilk2", fg="RoyalBlue4")
        self.level1_start_price_label.place(x=50, y=330)

        self.level1_product_des_frame = Frame(self.levels_info_frame, bg="cornsilk2")
        self.level1_product_des_frame.place(x=10, y=350)

        self.level1_product_des1 = Label(self.level1_product_des_frame, text="This wood is a porous and fibrous", bg="cornsilk2")
        self.level1_product_des2 = Label(self.level1_product_des_frame, text="structural tissue found in the", bg="cornsilk2")
        self.level1_product_des3 = Label(self.level1_product_des_frame, text="stems and roots of trees and", bg="cornsilk2")
        self.level1_product_des4 = Label(self.level1_product_des_frame, text="other woody plants.", bg="cornsilk2")
        self.level1_product_des5 = Label(self.level1_product_des_frame, text="It is an organic material – a natural", bg="cornsilk2")
        self.level1_product_des6 = Label(self.level1_product_des_frame, text="composite of cellulose fibers that", bg="cornsilk2")
        self.level1_product_des7 = Label(self.level1_product_des_frame, text="are strong in tension and embedded", bg="cornsilk2")
        self.level1_product_des8 = Label(self.level1_product_des_frame, text="in a matrix of lignin that resists", bg="cornsilk2")
        self.level1_product_des9 = Label(self.level1_product_des_frame, text="compression of any sort.", bg="cornsilk2")

        self.level1_product_des1.pack()
        self.level1_product_des2.pack()
        self.level1_product_des3.pack()
        self.level1_product_des4.pack()
        self.level1_product_des5.pack()
        self.level1_product_des6.pack()
        self.level1_product_des7.pack()
        self.level1_product_des8.pack()
        self.level1_product_des9.pack()

        self.lock_label = Label(self.levels_info_frame, image=self.lock_img)
        self.lock_label.place(x=5 + 60, y=5)

        # End Screen
        self.end_screen_frame = Frame(self.level_frame, bg="grey20")

        self.end_screen_label1 = Label(self.end_screen_frame, text="Level Passed", bg="grey20",
                                       font=self.end_screen_title_font, fg="ivory2")
        self.end_screen_label2 = Label(self.end_screen_frame, text="You have reached your profit goal!",
                                       bg="grey20", fg="ivory2")
        self.end_screen_label3 = Label(self.end_screen_frame, text="Game Over", bg="grey20",
                                       font=self.end_screen_title_font, fg="ivory2")
        self.end_screen_label4 = Label(self.end_screen_frame, text="You did not reach the profit goal!",
                                       bg="grey20", fg="ivory2")
        self.end_screen_label5 = Button(self.end_screen_frame, text="Continue", bg="grey20", fg="ivory2",
                                        command=lambda:self.close_end_screen())
        self.end_screen_profit_label = Label(self.end_screen_frame,
                                       bg="grey20", fg="ivory2", anchor=W)
        self.end_screen_xpgain_label = Label(self.end_screen_frame,
                                             bg="grey20", fg="ivory2", anchor=W)

        # Pause Button
        self.pause_button = Button(self.graph_frame, bd=0, image=self.pause_img, command=lambda: self.pause())
        self.pause_button.place(x=830, y=400, height=30, width=30)
        self.pause(True)

        # Mute Music Button
        self.mute_music_button = Button(self.graph_frame, bd=0, image=self.speaker_img, bg="grey69",
                                        command=lambda: self.mute_music())
        self.mute_music_button.place(x=20, y=400, height=30, width=30)

        # perc label
        self.perc_label = Label(self.graph_frame, bd=0, bg="grey69", text="Progress: {:.2f}%".format(0), font=self.price_font)
        self.perc_label.place(x=400, y=20)

        # Scale Widget
        self.speed_scale = Scale(self.level_frame, orient=HORIZONTAL, sliderlength=14, length=240, from_=0.1, to=0.008,
                                 showvalue=0, resolution=0.0001, troughcolor="white", repeatdelay=1000, bd=1,
                                 bg="grey10", label="Change the speed of the graph ↔", fg="white")
        self.speed_scale.set(self.line_delay)
        self.speed_scale.place(x=840, y=480)

        # Stock Price Label
        self.current_product = Product(0, 100)
        self.price_label = Label(self.graph_frame, bg="grey69", fg="black", text="Stock Price: £0", font=self.price_font,
                                 anchor=W)
        self.price_label.place(x=20, y=20, height=40, width=300)

        # Stock Multiplier
        self.stock_mult_button = Button(self.level_frame, bd=0, text=f"x{self.stock_mult_state}", font=self.stats_font,
                                        command=lambda: self.cycle_mult())
        self.stock_mult_button.place(x=260 + 128 + 30 + 200 + 55 + 120, y=480, height=20, width=40)

        # Buy/Sell line
        self.graph_canvas.create_line(self.buy_line, 0, self.buy_line, 450, width=2, fill="blue",
                                      tag="buy_line", dash=(3, 2))
        self.buy_line_label = Label(self.graph_frame, text="Buy/Sell Line", bg="grey69")
        self.buy_line_label.place(x=self.buy_line-33, y=10)

        # Spawn line
        self.graph_canvas.create_line(self.graph_boundary, 0, self.graph_boundary, 450, width=2, fill="black",
                                      tag="spawn_line", dash=(3, 2))
        self.spawn_line_label = Label(self.graph_frame, text="Spawn Line", bg="grey69")
        self.spawn_line_label.place(x=self.graph_boundary - 36, y=10)

        # Label 0 FPS DATASHEET
        self.fps_label = Label(self.datasheet.frame, bd=0)
        self.fps_label.pack()
        self.fps_label.config(text="")

        # Label 1 LINE COUNT DATASHEET
        self.label1 = Label(self.datasheet.frame)
        self.label1.pack()

        # Label 2 SCALE VALUE DATASHEET
        self.label2 = Label(self.datasheet.frame)
        self.label2.pack()

        # Label 3 MULT DATASHEET
        self.label3 = Label(self.datasheet.frame)
        self.label3.pack()

    def load_level(self):

        # Loads everything about the level

        self.load_all_events()  # loads all events from txt
        self.choose_events_for_level(amount=6)  # assigns 5 events for the level
        self.load_all_events_starting_ending_points()  # loads events start and end positions of events to the level
        self.create()  # loads all the lines in the level

    def load_all_events(self):  # loads all events from the file events.txt and creates all of them as objects

        with open("./resources/text/events.txt") as file:
            events = file.readlines()

        # STRIPS DATA IN FILE

        for event in events:
            evnt = event.strip("\n").split(":")
            evnt = Event(event_id=evnt[0], event_str=evnt[1], event_inf=float(evnt[2]), event_des=evnt[3], current_level=levels[0])

            self.all_events.append(evnt)

    def choose_events_for_level(self, amount):  # chooses a number of events to be embedded inside of the level

        self.level_events = random.sample(self.all_events, amount)

    def load_all_events_starting_ending_points(self):

        lines_amount = self.lines_amount  # the amount of lines being used in the level
        events_amount = len(self.level_events)  # the amount of events being used in the level

        quart_diff = (lines_amount / (events_amount + 1)) / 4

        for i, num in zip(range(events_amount), range(1, events_amount + 1)):
            self.level_events[i].load_start_and_end(lines_amount, events_amount, quart_diff, num)

    def create(self):  # creates a level using the basic instances, stores the level in self.lines_array

        line_count = 0

        for x in range(self.lines_amount):
            if not self.lines_array:  # if self.lines_array is empty or equal to []
                line = Line(lineID=x, colour=self.colour, startX=0, startY=225)

            else:
                last = self.lines_array[-1]
                line = Line(lineID=x, colour=self.colour, startX=last.endX, startY=last.endY)

            line.create_line(self.len_range, self.current_event_loading)
            self.lines_array.append(line)

            # CHECK IF LINE IS IN EVENT

            for i in range(len(self.level_events)):

                if line_count == int(self.level_events[i].start_line):
                    self.current_event_loading = self.level_events[i]
                    break

                elif line_count == int(self.level_events[i].end_line):
                    self.current_event_loading = None
                    break

            line_count += 1  # update index of line

    def start(self):  # plays the loaded content

        self.running = True
        self.pause(False)

        if not self.paused:

            # RESET VARIABLES

            time_start = time.time()  # fps timer start

            exceeded_total = 0
            self.line_count = 0  # for line index
            self.slideshow = False
            self.slideshow_trig = False
            self.speed_scale.config(state=DISABLED)
            self.graph_canvas.delete("line")
            self.start_bal = player.balance
            self.level_balance = self.start_bal
            self.level_balance_label.config(text=self.update_balance(self.level_balance))
            self.stocks_count = 0
            self.stocks_label.config(text=self.update_stock(self.stocks_count))
            self.restart_button.config(text="RESTART\nR")
            self.trans_log_listbox.delete(0, 9999)
            self.line_count = 0
            self.profit = 0
            self.profit_label.config(text="Profit\n{}{}/{}".format("", 0, self.profit_goal), fg="green2")
            self.graph_boundary = 800

            fps_start_time = time.time()  # start time of the loop
            fps_rate = 1
            fps_counter = 0

            # START LOOP

            while self.running:  # one cycle is one line spawned

                if not self.paused:

                    self.label1.config(text=f"Line count : {self.line_count}")

                    self.label2.config(text=f"Scale Value : {self.speed_scale.get()}")

                    elapsed = round(time.time() - time_start)  # find time elapsed from start of start() function

                    # CHECK IF NEXT LINE PASSES BOUNDARY

                    if self.lines_array[self.line_count].endX >= self.graph_boundary:  # if line spawned passes boundary

                        self.slideshow = True

                        exceeded_current = self.lines_array[self.line_count].endX - self.graph_boundary
                        # exceeded amount in virtual pixels past graph boundary

                        self.graph_boundary += exceeded_current
                        # calculate exceeded past boundary point and implement into new graph boundary
                        exceeded_total += exceeded_current

                        # Moves lines

                        self.graph_canvas.move("line", -exceeded_current, 0)

                    # SPAWNS NEXT LINE

                    self.lines_array[self.line_count].spawn_line(self.graph_canvas,
                                                                 exceeded_total)  # spawn current line in x loop
                    self.y_pos = (self.lines_array[self.line_count].endY * -1) + self.graph_canvas.winfo_height()
                    self.x_pos = self.lines_array[self.line_count].endX

                    if self.slideshow:

                        # ABLE SPEED SLIDER/SCALE

                        if not self.slideshow_trig:

                            self.slideshow_trig = True
                            self.speed_scale.config(state=NORMAL)
                            self.speed_scale.set(self.line_delay)


                        # ASSIGN i WITH BUY LINE endX VALUES

                        i = self.line_count - 20
                        self.speed = self.speed_scale.get()

                        while self.lines_array[i].endX - exceeded_total >= self.buy_line:
                            i = i - 1

                        self.current_product.current_price = (self.lines_array[i].endY * -1) + self.graph_canvas.winfo_height()

                    else:

                        self.current_product.current_price = self.y_pos
                        self.speed = 0.004

                    self.price_label.config(text=f"Stock Price: £{self.current_product.current_price}")
                    self.perc_label.config(text="Progress: {:.2f}%".format(self.get_perc()))

                    # CHECK IF LINE IS IN EVENT

                    for i in range(len(self.level_events)):

                        if self.line_count == int(self.level_events[i].start_line):
                            self.level_events[i].active = True
                            self.level_events[i].display()
                            self.current_event = self.level_events[i]
                            break

                        elif self.line_count == int(self.level_events[i].end_line):
                            self.level_events[i].active = False
                            self.level_events[i].remove()
                            self.current_event = self.level_events[i]
                            break

                    # update index of line
                    self.line_count += 1

                    # While loop to delay line spawning

                    start = time.time()

                    while time.time() - start < self.speed:  # temp delay to spawn next line

                        # STOCK LABEL COLOUR UPDATER ====================================================

                        self.stocks_label_flash()

                        # FPS LABEL UPDATER =============================================================

                        fps_counter += 1
                        if (time.time() - fps_start_time) > fps_rate:
                            fps = "FPS: {} ".format(round(fps_counter / (time.time() - fps_start_time)))
                            self.fps_label.config(
                                text=fps)  # updates fps
                            fps_counter = 0
                            fps_start_time = time.time()

                        # BUY LINE RETURN COLOUR ========================================================

                        try:  # checks if the timer has been triggered
                            elapsed = time.time() - self.buy_line_timer_start
                            if elapsed > 0.1:
                                self.graph_canvas.itemconfigure("buy_line", dash=(3, 2), fill="blue", width=2)
                        except:
                            pass

                        root.update()  # updates main window

                    if self.line_count > self.lines_amount - 1 or self.profit >= self.profit_goal:
                        self.running = False

                root.update()  # updates main window

            # LEVEL END

            if self.profit >= self.profit_goal:
                self.won = True
            else:
                self.won = False

            self.load_end_screen()

    def buy(self):

        if not self.paused and self.running and self.slideshow:

            if self.stocks_count == player.capacity:  # checks if stock count reached the capacity
                self.stocks_label.config(fg="orange red")
                self.stock_colour_timer_start = time.time()
                return

            elif self.stocks_count + self.stock_mult_state > player.capacity:

                mult = player.capacity - self.stocks_count

            else:

                mult = self.stock_mult_state

            # Plays Sound
            self.wood_sfx.play()

            # BOUGHT line
            #self.graph_canvas.create_line(0, 450, 900, 450, width=2, fill="red",
                                          #tag="bought_line", dash=(3, 2))

            # Change buy line colour
            self.graph_canvas.itemconfigure("buy_line", dash=None, fill="deep sky blue", width=2)
            self.buy_line_timer_start = time.time()

            # Updates buy/sell counters
            self.buy_count += mult
            self.sell_count = 0

            # Updates Balance
            self.level_balance -= self.current_product.current_price * mult
            self.transactions.append(self.level_balance)
            self.level_balance_label.config(text=self.update_balance(self.level_balance))
            player.balance = self.level_balance
            self.p_info_balance.config(text="Balance : £{}".format(player.balance))


            # Updates Listbox
            self.trans_log_listbox.insert(END,
                                  f"BOUGHT {self.buy_count}                               {self.current_product.current_price * mult}")
            self.trans_log_listbox.yview(END)

            # Updates Profit
            self.profit = self.level_balance - self.start_bal
            gain = "+" if self.profit > 0 else ""
            fg = "green2" if self.profit > 0 else "orange red"
            self.profit_label.config(text="Profit\n{}{}/{}".format(gain, self.profit, self.profit_goal), fg=fg, bg="grey10")
            # self.profit_label.place(x=260 + 40 + 300 + 80, y=476)

            # Updates Stock Count
            self.stocks_count += mult
            self.stocks_label.config(text=self.update_stock(self.stocks_count), fg="light blue")

    def sell(self):

        if not self.paused and self.running:

            # Checks if the stock count has reached 0 or the max capacity
            if self.stocks_count <= 0:
                self.stocks_label.config(fg="orange red")
                self.stock_colour_timer_start = time.time()
                return

            elif self.stocks_count - self.stock_mult_state < 0:

                mult = self.stocks_count

            else:

                mult = self.stock_mult_state

            # Plays Sound
            self.wood_sfx.play()

            # BOUGHT line
            #self.graph_canvas.create_line(0, 450, 900, 450, width=2, fill="red", dash=(3, 2))

            # Change buy line colour
            self.graph_canvas.itemconfigure("buy_line", dash=None, fill="deep sky blue", width=2)
            self.buy_line_timer_start = time.time()

            # Updates buy/sell counters
            self.sell_count += mult
            self.buy_count = 0

            # Updates Balance
            self.level_balance += self.current_product.current_price * mult
            self.transactions.append(self.level_balance)
            self.level_balance_label.config(text=self.update_balance(self.level_balance))
            player.balance = self.level_balance
            self.p_info_balance.config(text="Balance : £{}".format(player.balance))

            # Updates Listbox
            self.trans_log_listbox.insert(END,
                                  f"SOLD {self.sell_count}                                     {self.current_product.current_price * mult}")
            self.trans_log_listbox.yview(END)

            # Updates Profit
            self.profit = self.level_balance - self.start_bal
            gain = "+" if self.profit > 0 else ""
            fg = "green2" if self.profit > 0 else "orange red"
            self.profit_label.config(text="Profit\n{}{}/{}".format(gain, self.profit, self.profit_goal), fg=fg, bg="grey10")
            # self.profit_label.place(x=260 + 40 + 300 + 80, y=476)

            # Updates Stock Count
            self.stocks_count -= mult
            self.stocks_label.config(text=self.update_stock(self.stocks_count))

    def keyboard_pressed(self, event):

        key = event

        if key.char == "z":
            self.buy()

        elif key.char == "x":
            self.sell()

        elif key.char == "r":
            self.start()

        elif key.char == "p":
            self.pause()

        elif key.char == "m":
            self.mute_music()

        elif key.char == "t":
            self.cycle_mult()

        elif key.char == "`":
            self.datasheet.show()

        elif key.keysym == "Left":
            self.move_slider("left")

        elif key.keysym == "Right":
            self.move_slider("right")

    def mouse_pressed(self, event):

        self.mouse_pos = [event.x, event.y]

    def pause(self, state=None):

        if state is not None:

            self.paused = state

            if state is True:
                self.pause_button.config(image=self.play_img)
            elif state is False:
                self.pause_button.config(image=self.pause_img)

        elif not self.paused:  # paused status is switched on press

            self.pause_button.config(image=self.play_img)
            self.paused = True

        elif self.paused:

            self.pause_button.config(image=self.pause_img)
            self.paused = False

    def mute_music(self):

        if not self.muted_music:  # Switches music to volume 0

            pygame.mixer.music.set_volume(0)
            self.mute_music_button.config(image=self.speaker_muted_img)
            self.muted_music = True

        elif self.muted_music:  # sets music back to volume 0.1

            pygame.mixer.music.set_volume(0.1)
            self.mute_music_button.config(image=self.speaker_img)
            self.muted_music = False

    def move_slider(self, dir):

        if dir == "left":  # moves the slider a bit to the left or right when pressing left or right arrow on keyboard
            self.speed_scale.set(self.speed_scale.get() + 0.02)

        elif dir == "right":
            self.speed_scale.set(self.speed_scale.get() - 0.02)

    def show_p_info(self, state=None):

        if state is None:  # flips states
            if not self.showing_p_info:
                self.p_info_frame.place(x=70, y=20, width=220, height=600)
                self.p_info_button.config(font=self.button_font_underlined)
                self.showing_p_info = True

            elif self.showing_p_info:
                self.p_info_frame.place_forget()
                self.p_info_button.config(font=self.button_font)
                self.showing_p_info = False

        else:  # changes state to specified state
            if state:
                self.p_info_frame.place(x=70, y=20, width=220, height=600)
                self.p_info_button.config(font=self.button_font_underlined)
                self.showing_p_info = True

            elif not state:
                self.p_info_frame.place_forget()
                self.p_info_button.config(font=self.button_font)
                self.showing_p_info = False

    def show_trans_log(self, state=None):

        if state is None:  # flip the states
            if not self.showing_trans_log:
                self.trans_log_listbox.place(x=70, y=20, width=220, height=600)
                self.trans_log_listbox.yview_moveto(0.1)
                self.trans_log_listbox.yview(END)
                self.trans_log_button.config(font=self.button_font_underlined)
                self.showing_trans_log = True

            elif self.showing_trans_log:
                self.trans_log_listbox.place_forget()
                self.trans_log_button.config(font=self.button_font)
                self.showing_trans_log = False

        else:  # change state to specified state
            if state:
                self.trans_log_listbox.place(x=70, y=20, width=220, height=600)
                self.trans_log_listbox.yview_moveto(0.1)
                self.trans_log_listbox.yview(END)
                self.trans_log_button.config(font=self.button_font_underlined)
                self.showing_trans_log = True

            elif not state:
                self.trans_log_listbox.place_forget()
                self.trans_log_button.config(font=self.button_font)
                self.showing_trans_log = False

    def show_levels_info(self, state=None):

        if state is None:  # switch states to opposite state

            if not self.showing_levels_info:

                self.levels_info_frame.place(x=70, y=20, width=220, height=600)
                self.levels_info_button.config(font=self.button_font_underlined)
                self.showing_levels_info = True

            elif self.showing_levels_info:

                self.levels_info_frame.place_forget()
                self.levels_info_button.config(font=self.button_font)
                self.showing_levels_info = False

        else:  # switches state to the state specified

            if state:

                self.levels_info_frame.place(x=70, y=20, width=220, height=600)
                self.levels_info_button.config(font=self.button_font_underlined)
                self.showing_levels_info = True

            elif not state:

                self.levels_info_frame.place_forget()
                self.levels_info_button.config(font=self.button_font)
                self.showing_levels_info = False

    def change_tab(self, state=None, state2=None):

        if state is None:  # error handle
            raise Exception("no state given")

        elif state == "p_info":  # profile tab

            self.show_p_info(state2)
            self.show_trans_log(False)
            self.show_levels_info(False)

        elif state == "trans_log":  # transaction log tab

            self.show_trans_log(state2)
            self.show_p_info(False)
            self.show_levels_info(False)

        elif state == "levels_info":  # level information tab

            self.show_levels_info(state2)
            self.show_p_info(False)
            self.show_trans_log(False)

    def cycle_mult(self, custom_state=None):

        if custom_state is None:  # cycle through states if there is no specified state

            if self.stock_mult_state == 1:
                self.stock_mult_state = 10
                label = "x10"

            elif self.stock_mult_state == 10:
                self.stock_mult_state = 25
                label = "x25"

            elif self.stock_mult_state == 25:
                self.stock_mult_state = 100
                label = "x100"

            elif self.stock_mult_state == 100:
                self.stock_mult_state = 9999999
                label = "MAX"

            elif self.stock_mult_state == 9999999:
                self.stock_mult_state = 1
                label = "x1"

            else:
                label = "UNK"

        else:
            self.stock_mult_state = custom_state

            if custom_state == 9999999:
                label = "MAX"
            else:
                label = f"x{custom_state}"

        self.label3.config(text="Stock Mult State: {}".format(self.stock_mult_state))

        self.stock_mult_button.config(text=label)

    def stocks_label_flash(self):

        try:  # checks if the timer has been triggered and flashes when timer is under 1
            time_ = time.time() - self.stock_colour_timer_start
            if time_ > 1:
                self.stocks_label.config(fg="light blue")
        except:
            pass

    def load_end_screen(self):

        if self.won:  # checks if player has won or lost the game

            self.end_screen_frame.place(x=600-250, y=100, height=400, width=500)
            self.end_screen_frame.tkraise()

            self.end_screen_label3.place_forget()
            self.end_screen_label4.place_forget()

            self.end_screen_label1.place(x=40, y=20)
            self.end_screen_label2.place(x=40, y=90)
            self.end_screen_label5.place(x=40, y=340)

            self.end_screen_profit_label.config(text="Profit Earned: +{}\nTotal Balance: £{}".format(self.profit, player.balance))
            self.end_screen_profit_label.place(x=40, y=90 + 30)

            player.xp += 10
            self.p_info_xp.config(text="XP : {}".format(player.xp))
            self.end_screen_xpgain_label.config(text="XP Earned: +{}\nTotal XP: {}".format(10, player.xp))
            self.end_screen_xpgain_label.place(x=40, y=90 + 30 + 30)

        else:  # player has lost the game

            self.end_screen_frame.place(x=600 - 250, y=100, height=400, width=500)
            self.end_screen_frame.tkraise()

            self.end_screen_label1.place_forget()
            self.end_screen_label2.place_forget()
            self.end_screen_profit_label.place_forget()
            self.end_screen_xpgain_label.place_forget()

            self.end_screen_label3.place(x=40, y=20)
            self.end_screen_label4.place(x=40, y=90)
            self.end_screen_label5.place(x=40, y=340)

    def close_end_screen(self):  # closes the end screen frame
        self.end_screen_frame.place_forget()

    def get_perc(self):  # returns the percentage amount into the level going closed to 100% as the level plays out
        perc = (self.line_count/self.lines_amount)*100
        return perc


class Product(Level):  # Connects level to database and locates product eg wood

    def __init__(self, id, original_price):

        database.connect(path="./databases/products.db")

        self.product_id = id
        self.original_price = original_price
        self.current_price = self.original_price

        database.cur.execute("SELECT * FROM Origin")


class Line(Level):  #

    def __init__(self, lineID, colour, startX=0, startY=225, endX=0,
                 endY=0):  # 225 is half of the ceiling height which is 450

        self.lineID = lineID
        self.colour = colour
        self.startX = startX
        self.startY = startY
        self.endX = endX
        self.endY = endY

    def create_line(self, length_range, current_event_loading):  # creates and updates the line start and end coordinate

        # create_line() happens during loading phase of the level

        if current_event_loading is None:
            event_inf = 1
        else:
            event_inf = float(current_event_loading.inf)

        startX, startY = self.startX, self.startY
        rand_x = random.randint(length_range[0], length_range[1])
        rand_y = random.randint(length_range[0], length_range[1])

        height_perc = int((startY / 450) * 100)  # 450 is the height of the ceiling
        inf = height_perc * event_inf

        if random.randint(0, 100) < inf:
            # % chance to flip rand_y value to negative
            rand_y *= -1

        endX, endY = startX + rand_x, startY + rand_y

        # assigns the object lines their vector positions
        self.startX, self.startY, self.endX, self.endY = startX, startY, endX, endY

    def spawn_line(self, graph_canvas, exceeded_total=0):
        graph_canvas.create_line(self.startX - exceeded_total, self.startY, self.endX - exceeded_total,
                                 self.endY, width=1.5, fill=self.colour, tags="line")


class Event(Level):

    def __init__(self, event_id, event_str, event_inf, event_des, current_level):

        self.current_level = current_level

        self.id = event_id
        self.str = event_str
        self.inf = event_inf
        self.des = event_des
        self.start_line = None
        self.end_line = None
        self.active = False
        self.remove()

    def load_start_and_end(self, lines_amount, events_amount, quart_diff, event_number):
        # uses a formulae to calculate the duration, starting and ending point of an event

        half_line = (lines_amount / (events_amount + 1)) * event_number

        self.start_line = half_line - quart_diff
        self.end_line = half_line + quart_diff

    def display(self):
        # displays event string in textbox

        self.current_level.event_textbox.config(state=NORMAL)
        self.current_level.event_textbox.delete(1.0, END)
        self.current_level.event_textbox.insert(INSERT, self.str)
        self.current_level.event_textbox.config(state=DISABLED)

        self.current_level.event_textbox.tag_add("Rising", 1.0, END)
        self.current_level.event_textbox.tag_config("Rising", background="lawn green" if self.inf > 1 else "orange red")

    def remove(self):

        # removes event from being displayed in textbox
        self.current_level.event_textbox.config(state=NORMAL)
        self.current_level.event_textbox.delete(1.0, END)
        self.current_level.event_textbox.insert(INSERT, "No current event!")
        self.current_level.event_textbox.config(state=DISABLED)


def open_level():
    global root, player, datasheet

    # CONSTRUCT WINDOW

    root = Tk()

    root.title("Stock Universe!")
    root.geometry("{}x{}".format("1200", "700"))
    root.resizable(0, 0)
    root.overrideredirect(False)
    root.protocol("WM_DELETE_WINDOW", quit_)
    root.iconbitmap("./resources/textures/icon.ico")

    # DEV CAN SWITCH TO DEV MODE

    try: player = Player(username=login.username, player_key=login.player_key)
    except: player = Player(username="Developer", dev_key=True)

    # LOAD LEVEL

    level1 = Level(level_id=0, level_diff=1, line_delay=0.06, lines_amount=8000, colour="blue",
                  len_range=[3, 5], profit_goal=8000)  # constructs level as an object, [3, 5]
    levels.append(level1)  # adds the level to the levels list
    current_level = level1


    #level2 = Level(level_id=1, level_diff=2, line_delay=0.06, lines_amount=9000, colour="red",
    #               len_range=[5, 9], profit_goal=10000)  # constructs level as an object, [5,9]
    #levels.append(level2)  # adds the level to the levels list

    current_level.load_level()  # loads the level
    #levels[0].load_level()  # loads the level



    # RUN MAIN LOOP

    root.mainloop()


def open_login():
    global login

    login = Login(database, tkinter)
    if login.login_successful:
        open_level()


def quit_():
    print("e")
    root.destroy()
    sys.exit()


def pass_func():
    pass


if __name__ == "__main__":
    database = Database(sqlite3)
    levels = []
    current_level = None
    pygame.init()
    open_login()
