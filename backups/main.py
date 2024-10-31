from tkinter import *
import pygame
import random
import time
import sqlite3
import threading
from PIL import ImageTk,Image

class Login:

    def __init__(self):

        self.login_successful = False
        self.login_status = "Not Logged In"

        self.frame = Frame(log_win, bg="lavender")
        self.frame.place(x=0, y=0, height=400, width=600)
        self.check_entries_button = Button(self.frame, bd=1, command=lambda: self.check_entries())
        self.register_button = Button(self.frame, text="REGISTER", bd=0, bg="firebrick1",
                                      command=lambda: self.register())
        self.login_button = Button(self.frame, text="LOGIN", bd=0, bg="firebrick1", command=lambda: self.login())
        self.u_entry = Entry(self.frame, text="Enter username")
        self.p_entry = Entry(self.frame, text="Enter password", show="•")
        self.back_button = Button(self.frame, text="<-", command=lambda: self.main_menu(), bd=1)
        self.status_label = Label(self.frame, text=self.login_status, bg="lavender")
        self.status_label.place(x=200, y=20)
        self.play_button = Button(self.frame, text="PLAY GAME", bd=0, bg="firebrick1", command=lambda: self.play())
        self.play_button.place(x=200, y=100 + 60 + 10 + 60 + 10, height=60, width=200)
        self.main_menu()

    def main_menu(self):

        self.state = "main_menu"
        self.play_button.place(x=200, y=100 + 60 + 10 + 60 + 10, height=60, width=200)
        self.back_button.place_forget()
        self.check_entries_button.place_forget()
        self.u_entry.place_forget()
        self.p_entry.place_forget()
        self.register_button.place(x=200, y=100, height=60, width=200)
        self.login_button.place(x=200, y=100 + 60 + 10, height=60, width=200)
        self.status_label.config(text=self.login_status, fg="black")

    def register(self):

        self.state = "register"
        self.play_button.place_forget()
        self.u_entry.delete(0, 999)
        self.p_entry.delete(0, 999)
        self.back_button.place(x=20, y=20)
        self.check_entries_button.config(text="REGISTER NOW")
        self.check_entries_button.place(x=300-50, y=230, height=20, width=100)
        self.register_button.place_forget()
        self.login_button.place_forget()
        self.u_entry.place(x=200, y=100, height=30, width=200)
        self.p_entry.place(x=200, y=100 + 50, height=30, width=200)

    def login(self):

        self.state = "login"
        self.play_button.place_forget()
        self.u_entry.delete(0, 999)
        self.p_entry.delete(0, 999)
        self.back_button.place(x=20, y=20)
        self.check_entries_button.config(text="LOGIN NOW")
        self.check_entries_button.place(x=300-50, y=230, height=20, width=100)
        self.register_button.place_forget()
        self.login_button.place_forget()
        self.u_entry.place(x=200, y=100, height=30, width=200)
        self.p_entry.place(x=200, y=100 + 50, height=30, width=200)

    def exists(self, username):

        conn = sqlite3.connect("./databases/logins.db")  # connects to database
        cur = conn.cursor()

        cur.execute("SELECT username FROM Accounts")  # gets all usernames in database
        usernames = []
        for x in cur.fetchall():
            usernames.append(x[0])

        for x in usernames:
            if x == username:
                conn.close()
                return True

        return False

    def check_entries(self):

        conn = sqlite3.connect("./databases/logins.db")  # connects to database
        cur = conn.cursor()

        cur.execute("CREATE TABLE IF NOT EXISTS Accounts(username VARCHAR(16), password VARCHAR(16), player_key INT)")
        conn.commit()

        u_input = self.u_entry.get()
        p_input = self.p_entry.get()

        if self.state == "register":

            if not (3 <= len(u_input) <= 16):
                self.status_label.config(text="Username must be between 3 and 16 characters", fg="red")
                #self.flash_red(self.status_label)

            elif self.exists(u_input):
                self.status_label.config(text="Username already exists", fg="red")
                #self.flash_red(self.status_label)

            else:
                self.status_label.config(text="Account Registered", fg="black")
                cur.execute("INSERT INTO Accounts(username,password) VALUES(?,?)", (u_input, p_input))
                conn.commit()
                self.u_entry.delete(0, 999)
                self.p_entry.delete(0, 999)

        elif self.state == "login":

            self.u_entry.delete(0, 999)
            self.p_entry.delete(0, 999)

            cur.execute("SELECT username FROM Accounts")  # gets all usernames in database
            usernames = []
            for x in cur.fetchall():
                usernames.append(x[0])

            cur.execute("SELECT password FROM Accounts")  # gets all passwords in database
            passwords = []
            for x in cur.fetchall():
                passwords.append(x[0])

            for i in range(len(usernames)):
                if u_input == usernames[i]:
                    if p_input == passwords[i]:
                        self.username = usernames[i]
                        self.password = passwords[i]
                        self.login_successful = True
                        self.login_status = "Logged in as: {}".format(self.username)
                        self.status_label.config(text=self.login_status, fg="black")
                        break

            if not self.login_successful: # if username does not match password
                self.status_label.config(text="Incorrect username or password", fg="red")

        conn.close()

    def play(self):

        if self.login_successful:
            log_win.destroy()
            open_level()
        else:
            self.status_label.config(text="Must be logged in to play", fg="red")


class Player:

    def __init__(self, username="Guest"):
        self.level = 0
        self.xp = 0
        self.username = username

        # Widgets

        self.frame = Frame(root, bg="blue", bd=1)
        self.frame.place(x=10, y=20, height=450, width=200)

        self.username_label = Label(self.frame, text=self.username, fg="light blue")
        self.username_label.place(x=5, y=5)


class Level:

    def __init__(self, level_id, level_diff, line_delay, lines_amount, colour="black", len_range=[1,2],
                 lines_array=[]):  # make an object that has the basics to create a level

        self.running = False

        self.level_id = level_id  # this is the primary key for each level layout that does not change
        self.level_diff = level_diff  # level difficulty
        self.line_delay = line_delay  # the time it takes for each line to spawn
        self.lines_amount = lines_amount  # the amount of lines
        self.lines_array = lines_array  # lines layout in object form
        self.lines_array_raw = []  # raw numbers and values in an array of tuples
        self.slideshow = False  # boolean to represent graph moving to the left
        self.graph_boundary = 800 # pixels from left to right  on the graph until slideshow starts
        self.transactions = [] # a list that stores the history of transactions that have been made during the level
        self.level_balance = 500 # the balance of the player in the level start (500)
        self.transactions.append(self.level_balance) # starting transaction is always what you start with
        self.y_pos = 0
        self.x_pos = 0
        self.mouse_pos = []
        self.pause(True)
        self.buy_count = 0
        self.sell_count = 0
        self.colour = colour
        self.len_range = len_range
        self.all_events = []
        self.level_events = []
        self.current_event_id_loading = None
        self.current_event_id = None

        # Load Textures ================================================================================================

        self.power_img = ImageTk.PhotoImage(Image.open("./resources/textures/power.png"))

        # Widgets ======================================================================================================

        # Main Level Frame
        self.level_frame = Frame(root, relief=FLAT, cursor="circle", bd=0)
        self.level_frame.place(x=0, y=0)

        # Background canvas
        self.bg = Canvas(self.level_frame, bg="grey10", width=1300,
                         height=700, bd=0)
        self.bg.grid(row=0, column=0)

        # Graph frame at x=350, y=20
        self.graph_frame = Frame(self.level_frame, cursor="plus", bd=0)
        self.graph_frame.place(x=300, y=20, height=450, width=880)

        # Graph canvas
        self.graph_canvas = Canvas(self.graph_frame, bg="grey70", bd=0)
        self.graph_canvas.place(x=0, y=0, height=450, width=880)

        # Key binds
        root.bind("<Key>", self.keyboard_pressed)
        self.level_frame.bind("<Button-1>", self.mouse_pressed)

        # Buy Frame
        self.buy_frame = Frame(self.level_frame, bd=0)
        self.buy_frame.place(x=260 + 128 + 30 + 200, y=490+70, height=90, width=90)

        # Sell Frame
        self.sell_frame = Frame(self.level_frame, bd=0)
        self.sell_frame.place(x=260 + 128 + 30 + 200 + 90 + 10, y=490+70, height=90, width=90)

        # Buy Button
        self.buy_button = Button(self.buy_frame, bd=0, bg="lawn green", text="BUY\n\nZ", command=lambda: self.buy())
        self.buy_button.place(x=0, y=0, height=90, width=90)

        # Sell Button
        self.sell_button = Button(self.sell_frame, bd=0, bg="lawn green", text="SELL\n\nX", command=lambda: self.sell())
        self.sell_button.place(x=0, y=0, height=90, width=90)

        # Restart Button
        self.restart_button = Button(self.level_frame, bd=0, bg="lawn green", text="START\nR",
                                     command=lambda: self.start())
        self.restart_button.place(x=1100, y=490 + 70, height=40, width=50)

        # Quit Button
        self.quit = Button(self.level_frame, bd=0,image=self.power_img, command=lambda: root.destroy())
        self.quit.place(x=1160, y=670)

        # Timer elapsed Label
        self.timer_label = Label(self.graph_frame, bg="grey70", text="0 seconds")
        self.timer_label.place(x=10, y=10, height=32, width=64)

        # Balance Label
        self.level_balance_label = Label(self.level_frame, bg="grey10", fg="light blue", )
        self.level_balance_label.place(x=260 + 128 + 30 + 200, y=480, height=25, width=50)

        # Profit label
        self.profit_label = Label(self.level_frame)

        # Stocks Counter label
        self.stocks_label = Label(self.level_frame, bg="grey10", fg="light blue")
        self.stocks_label.place(x=260 + 128 + 30 + 200, y=480 + 40, height=25, width=50)

        # Current Event Textbox
        self.event_textbox_frame = Frame(self.level_frame)
        self.event_textbox_frame.place(x=260 + 40, y=480, width=300, height=170)
        self.event_textbox = Text(self.event_textbox_frame, state=DISABLED)
        self.event_textbox.place(x=0, y=0, width=300, height=170)

        # ListBox
        self.listbox = Listbox(self.level_frame, bd=0, bg="grey36", fg="light blue")
        self.listbox.place(x=20, y=20, width=250, height=600)
        self.listbox.yview_moveto(0.1)

        # FPS counter
        self.fps_label = Label(self.level_frame)
        self.fps_label.place(x=1100, y=20)
        self.fps_label.config(text="60")

        # Pause Button
        self.pause_button = Button(self.level_frame, bd=0, fg="white", bg="grey10", command=lambda: self.pause())
        self.pause_button.place(x=1100, y=490, height=40, width=40)

        # Buy/Sell line

        buy_sell_line = self.graph_canvas.create_line(20, 20, 40, 40, width=2, fill="red", tags="buyLine")

    def load_all_events(self):  # loads all events from the file events.txt and creates all of them as objects

        with open("./resources/text/events.txt") as file:
            events = file.readlines()

        # STRIPS DATA IN FILE

        for event in events:
            evnt = event.strip("\n").split(":")
            evnt = Event(event_id=evnt[0], event_str=evnt[1], event_inf=evnt[2], event_des=evnt[3])

            self.all_events.append(evnt)

        # ========================================================================================================

        self.choose_events_for_level(5)  # 5 is the amount of events being chosen for the level to contain

    def choose_events_for_level(self, amount):  # chooses a number of events to be embedded inside of the level

        choice = random.choice(self.all_events)
        self.level_events.append(choice)

    def create(self):  # creates a level using the basic instances, stores the level in self.lines_array

        self.load_all_events()
        line_count = 0

        for x in range(self.lines_amount):
            if not self.lines_array:  # if self.lines_array is empty or equal to []
                line_count += 1
                line = Line(lineID=x, colour=self.colour, startX=0, startY=225)

            else:
                line_count += 1
                last = self.lines_array[-1]
                line = Line(lineID=x, colour=self.colour, startX=last.endX, startY=last.endY)
            #self.
            #line_count >=
            line.create_line(self.len_range)
            # print(line.startX,line.startY,line.endX,line.endY)
            self.lines_array.append(line)

    def start(self):  # plays the loaded content

        self.running = True
        self.pause(False)

        if not self.paused:

            time_start = time.time()

            exceeded_total = 0
            line_count = 0
            temp_count = 0

            self.graph_canvas.delete("line")
            self.start_bal = 500
            self.level_balance = self.start_bal
            self.level_balance_label.config(text="Balance:\n£{}".format(self.level_balance))
            self.stocks_count = 0
            self.stocks_label.config(text="Stocks:\n{}".format(self.stocks_count))
            self.restart_button.config(text="RESTART\nR")
            self.listbox.delete(0,9999)
            self.line_count = 0

            self.profit = 0
            self.graph_boundary = 800

            while self.running:  # one cycle is one line spawned

                if not self.paused:

                    fps_start_time = time.time()  # start time of the loop

                    elapsed = round(time.time() - time_start)  # find time elapsed from start of start() function
                    self.timer_label.config(
                        text="{} seconds".format(elapsed))  # update label telling the elapsed time

                    try: # checks if the timer has been triggered
                        self.stock_colour_timer_elapsed = time.time()-self.stock_colour_timer_start
                        if self.stock_colour_timer_elapsed > 1:
                            self.stocks_label.config(fg="light blue")
                    except:
                        pass

                    if self.lines_array[line_count].endX >= self.graph_boundary:  # if line spawned passes boundary

                        self.slideshow = True

                        exceeded_current = self.lines_array[line_count].endX - self.graph_boundary
                        # exceeded amount in virtual pixels past graph boundary

                        self.graph_boundary += exceeded_current
                        # calculate exceeded past boundary point and implement into new graph boundary
                        exceeded_total += exceeded_current

                        self.graph_canvas.delete('line')  # delete all lines in graph canvas

                        for y in range(line_count - 300, line_count):
                            # loops through all lines already spawned on the graph -170 in order to move them to the left
                            self.lines_array[y].spawn_line(self.graph_canvas, exceeded_total)

                    self.lines_array[line_count].spawn_line(self.graph_canvas)  # spawn current line in x loop
                    self.y_pos = (self.lines_array[line_count].endY * -1) + 490
                    self.x_pos = self.lines_array[line_count].endX
                    self.current_product_price = self.y_pos
                    line_count += 1

                    #time.sleep(self.line_delay)

                    start = time.time()

                    while time.time()-start < self.line_delay:

                        root.update()  # updates main window

                root.update()  # updates main window
                temp_count += 1
                #print(temp_count)

                self.fps_label.config(text=f"FPS: {int(1.0 / (time.time() - fps_start_time))}")  # FPS = 1 / time to process loop

    def buy(self):

        if not self.paused:

            # Set Values
            self.buy_count += 1
            self.sell_count = 0

            # Updates Balance
            self.level_balance -= self.current_product_price
            self.transactions.append(self.level_balance)
            self.level_balance_label.config(text="Balance:\n£{}".format(self.level_balance),
                                      fg="lawn green" if self.level_balance > self.start_bal else "orange red")

            # Updates Listbox
            self.listbox.insert(END, f"buy count: {self.buy_count} ;                             {self.level_balance}")
            self.listbox.yview(END)

            # Updates Stock Count
            self.stocks_count += 1
            self.stocks_label.config(text="Stocks:\n{}".format(self.stocks_count), fg="light blue")

    def sell(self):

        if not self.paused:

            if self.stocks_count <= 0:
                self.stocks_label.config(fg="orange red")
                self.stock_colour_timer_start = time.time()
                return

            self.sell_count += 1
            self.buy_count = 0

            # Updates Balance
            self.level_balance += self.current_product_price
            self.transactions.append(self.level_balance)
            self.level_balance_label.config(text="Balance:\n£{}".format(self.level_balance),
                                          fg="lawn green" if self.level_balance > self.start_bal else "orange red")

            # Updates Listbox
            self.listbox.insert(END, f"sell count: {self.sell_count} ;                             {self.level_balance}")
            self.listbox.yview(END)

            # Updates Profit
            self.profit = self.transactions[-self.buy_count]
            gain = "+" if self.profit > 0 else ""
            fg = "green2" if self.profit > 0 else "orange red"
            self.profit_label.config(text="{}{}".format(gain, self.profit), fg=fg, bg="grey10")
            self.profit_label.place(x=260 + 40 + 300 + 80, y=480)

            # Updates Stock Count
            self.stocks_count -= 1
            self.stocks_label.config(text="Stocks:\n{}".format(self.stocks_count))

    def keyboard_pressed(self, event):

        key = event.keysym
        if key == "z":
            self.buy()

        elif key == "x":
            self.sell()

        elif key == "r":
            self.start()

        elif key == "p":
            self.pause()

    def mouse_pressed(self, event):

        self.mouse_pos = [event.x, event.y]
        print(self.mouse_pos)

    def pause(self, state=None):

        if state is not None:

            self.paused = state

        elif not self.paused:  # paused status is switched on press

            self.pause_button.config(text="⏸")
            self.paused = True

        elif self.paused:

            self.pause_button.config(text="⏵")
            self.paused = False


class Product(Level):

    def __init__(self, id, orgnl_prc, crrnt_prc):

        self.product_id = id
        self.original_price = orgnl_prc
        self.current_price = crrnt_prc

        self.price_label = Label()

    def display_product_name(self):

        label = Label(self.level_frame, text="'product'")
        label.place()

    def database_init(self):

        cur.execute("CREATE TABLE IF NOT EXISTS Origin(player_key PRIMARY_KEY INT, password VARCHAR(16))")
        conn.commit()


class Line(Level):

    def __init__(self, lineID, colour, startX=0, startY=225, endX=0, endY=0): # 225 is half of the ceiling height which is 450

        self.lineID = lineID
        self.colour = colour
        self.startX = startX
        self.startY = startY
        self.endX = endX
        self.endY = endY

    def create_line(self, length_range):  # creates and updates the line start and end coordinates

        startX, startY = self.startX, self.startY
        rand_x = random.randint(length_range[0], length_range[1])
        rand_y = random.randint(length_range[0], length_range[1])

        inf = int((startY / 450) * 100)  # 450 is the height of the ceiling
        #inf = inf * self.current_event_loading.inf

        if random.randint(0, 100) < inf: rand_y *= -1  # 50% chance to flip rand_y value to negative

        endX, endY = startX + rand_x, startY + rand_y

        self.startX, self.startY, self.endX, self.endY = startX, startY, endX, endY  # assigns the object lines their vector positions

    def spawn_line(self, graph_canvas, exceeded_total=0):

        graph_canvas.create_line(self.startX - exceeded_total, self.startY, self.endX - exceeded_total, self.endY,
                                 width=1.5, fill=self.colour, tags="lineTag")


class Event(Level):

    def __init__(self, event_id, event_str, event_inf, event_des):

        self.id = event_id
        self.str = event_str
        self.inf = event_inf
        self.des = event_des

    def load_start_and_end(self):  # uses a formulae to calcualte the duration, starting and ending point of an event

        lines_amount = len(self.lines_array)  # the amount of lines being used in the level
        events_amount = len()

        self.start_line
        
    def display(self):  # displays event string in textbox

        pass

    def update(self):

        pass


def open_level():

    global root, player, level

    root = Tk()

    root.title("Stock Universe!")
    root.geometry("{}x{}".format("1200", "700"))
    root.resizable(0, 0)

    try:
        player = Player(username=login.username)
    except:
        player = Player(username="developer")

    level = Level(level_id=0, level_diff=3, line_delay=0.04, lines_amount=15000, colour="blue", len_range=[3,6])  # constructs level as an object
    level.create()  # creates the lines of the level

    #threadInit()

    root.mainloop()


def threadInit():

    pass


def open_login():

    global log_win, login

    log_win = Tk()

    log_win.title("Login")
    log_win.geometry("{}x{}".format("600", "400"))
    log_win.resizable(0, 0)

    login = Login()

    log_win.mainloop()

if __name__ == "__main__":

    open_level()
