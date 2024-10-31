from tkinter import *
import pygame
import random
import time
import sqlite3
import threading
from PIL import ImageTk, Image
CLASS Login:
    FUNCTION __init__(self):
         login_successful <- False
         login_status <- "Not Logged In"
         frame <- Frame(log_win, bg="lavender")
         frame.place(x=0, y=0, height=400, width=600)
         check_entries_button <- Button( frame, bd=1, command=lambda:  check_entries())
         register_button <- Button( frame, text="REGISTER", bd=0, bg="firebrick1",
                                      command=lambda:  register())
         login_button <- Button( frame, text="LOGIN", bd=0, bg="firebrick1", command=lambda:  login())
         u_entry <- Entry( frame, text="Enter username")
         p_entry <- Entry( frame, text="Enter password", show="•")
         back_button <- Button( frame, text="<-", command=lambda:  main_menu(), bd=1)
         status_label <- Label( frame, text= login_status, bg="lavender")
         status_label.place(x=200, y=20)
         play_button <- Button( frame, text="PLAY GAME", bd=0, bg="firebrick1", command=lambda:  play())
         play_button.place(x=200, y=100 + 60 + 10 + 60 + 10, height=60, width=200)
         main_menu()
    ENDFUNCTION

    FUNCTION main_menu(self):
         state <- "main_menu"
         play_button.place(x=200, y=100 + 60 + 10 + 60 + 10, height=60, width=200)
         back_button.place_forget()
                               ENDFOR
         check_entries_button.place_forget()
                                        ENDFOR
         u_entry.place_forget()
                           ENDFOR
         p_entry.place_forget()
                           ENDFOR
         register_button.place(x=200, y=100, height=60, width=200)
         login_button.place(x=200, y=100 + 60 + 10, height=60, width=200)
         status_label.config(text= login_status, fg="black")
    ENDFUNCTION

    FUNCTION register(self):
         state <- "register"
         play_button.place_forget()
                               ENDFOR
         u_entry.delete(0, 999)
         p_entry.delete(0, 999)
         back_button.place(x=20, y=20)
         check_entries_button.config(text="REGISTER NOW")
         check_entries_button.place(x=300 - 50, y=230, height=20, width=100)
         register_button.place_forget()
                                   ENDFOR
         login_button.place_forget()
                                ENDFOR
         u_entry.place(x=200, y=100, height=30, width=200)
         p_entry.place(x=200, y=100 + 50, height=30, width=200)
    ENDFUNCTION

    FUNCTION login(self):
         state <- "login"
         play_button.place_forget()
                               ENDFOR
         u_entry.delete(0, 999)
         p_entry.delete(0, 999)
         back_button.place(x=20, y=20)
         check_entries_button.config(text="LOGIN NOW")
         check_entries_button.place(x=300 - 50, y=230, height=20, width=100)
         register_button.place_forget()
                                   ENDFOR
         login_button.place_forget()
                                ENDFOR
         u_entry.place(x=200, y=100, height=30, width=200)
         p_entry.place(x=200, y=100 + 50, height=30, width=200)
    ENDFUNCTION

    FUNCTION exists(self, username):
        conn <- sqlite3.connect("./databases/logins.db")  # connects to database
        cur <- conn.cursor()
        cur.execute("SELECT username FROM Accounts")  # gets all usernames in database
        usernames <- []
        for x in cur.fetchall():
            usernames.append(x[0])
        ENDFOR
        for x in usernames:
            IF x = username:
                conn.close()
                RETURN True
            ENDIF
        ENDFOR
        RETURN False
    ENDFUNCTION

    FUNCTION check_entries(self):
        conn <- sqlite3.connect("./databases/logins.db")  # connects to database
        cur <- conn.cursor()
        cur.execute("CREATE TABLE IF NOT EXISTS Accounts(username VARCHAR(16), password VARCHAR(16), player_key INT)")
        conn.commit()
        u_input <-  u_entry.get()
        p_input <-  p_entry.get()
        IF  state = "register":
            IF not (3 <= len(u_input) <= 16):
                 status_label.config(text="Username must be between 3 AND 16 characters", fg="red")
                #  flash_red( status_label)
            ELSEIF  exists(u_input):
                 status_label.config(text="Username already exists", fg="red")
                #  flash_red( status_label)
            ELSE:
                 status_label.config(text="Account Registered", fg="black")
                cur.execute("INSERT INTO Accounts(username,password) VALUES(?,?)", (u_input, p_input))
                conn.commit()
                 u_entry.delete(0, 999)
                 p_entry.delete(0, 999)
            ENDIF
        ELSEIF  state = "login":
             u_entry.delete(0, 999)
             p_entry.delete(0, 999)
            cur.execute("SELECT username FROM Accounts")  # gets all usernames in database
            usernames <- []
            for x in cur.fetchall():
                usernames.append(x[0])
            ENDFOR
            cur.execute("SELECT password FROM Accounts")  # gets all passwords in database
            passwords <- []
            for x in cur.fetchall():
                passwords.append(x[0])
            ENDFOR
            for i in range(len(usernames)):
                IF u_input = usernames[i]:
                    IF p_input = passwords[i]:
                         username <- usernames[i]
                         password <- passwords[i]
                         login_successful <- True
                         login_status <- "Logged in as: {}".format( username)
                                                               ENDFOR
                         status_label.config(text= login_status, fg="black")
                        break
                ENDIF
                    ENDIF
            ENDFOR
            IF not  login_successful:  # IF username does not match password
                 status_label.config(text="Incorrect username or password", fg="red")
        ENDIF
            ENDIF
        conn.close()
    ENDFUNCTION

    FUNCTION play(self):
        IF  login_successful:
            log_win.destroy()
            open_level()
        ELSE:
             status_label.config(text="Must be logged in to play", fg="red")
        ENDIF
    ENDFUNCTION

ENDCLASS

CLASS Player:
    FUNCTION __init__(self, username="Guest"):
         level <- 0
         xp <- 0
         username <- username
        # Widgets
         frame <- Frame(root, bg="blue", bd=1)
         frame.place(x=10, y=20, height=450, width=200)
         username_label <- Label( frame, text= username, fg="light blue")
         username_label.place(x=5, y=5)
    ENDFUNCTION

ENDCLASS

CLASS Level:
    FUNCTION __init__(self, level_id, level_diff, line_delay, lines_amount, len_range, colour="black",
                                        ENDIF
                 lines_array=[]):  # make an object that has the basics to create a level
         running <- False
         level_id <- level_id  # this is the primary key for each level layout that does not change
                                                            ENDFOR
         level_diff <- level_diff  # level difficulty
                    ENDIF
         line_delay <- line_delay  # the time it takes for each line to spawn
                                                          ENDFOR
         lines_amount <- lines_amount  # the amount of lines
         lines_array <- lines_array  # lines layout in object form
                                                                 ENDFOR
         lines_array_raw <- []  # raw numbers AND values in an array of tuples
         slideshow <- False  # boolean to represent graph moving to the left
         graph_boundary <- 800  # pixels from left to right  on the graph until slideshow starts
         transactions <- []  # a list that stores the history of transactions that have been made during the level
         level_balance <- 500  # the balance of the player in the level start (500)
         transactions.append( level_balance)  # starting transaction is always what you start with
         y_pos <- 0
         x_pos <- 0
         mouse_pos <- []
         pause(True)
         buy_count <- 0
         sell_count <- 0
         colour <- colour
         len_range <- len_range
         all_events <- []
         level_events <- []
         current_event_id_loading <- None
         current_event_id <- None
         times_font <- ("Times", "10", "bold roman")
        # Load Textures ================================================================================================
         power_img <- ImageTk.PhotoImage(Image.open("./resources/textures/power.png"))
         play_img <- ImageTk.PhotoImage(Image.open("./resources/textures/play.png"))
         pause_img <- ImageTk.PhotoImage(Image.open("./resources/textures/pause.png"))
        # Widgets ======================================================================================================
        # Main Level Frame
         level_frame <- Frame(root, relief=FLAT, cursor="circle", bd=0)
         level_frame.place(x=0, y=0)
        # Background canvas
         bg <- Canvas( level_frame, bg="grey10", width=1300,
                         height=700, bd=0)
         bg.grid(row=0, column=0)
        # Graph frame at x=350, y=20
         graph_frame <- Frame( level_frame, cursor="plus", bd=0)
         graph_frame.place(x=300, y=20, height=450, width=880)
        # Graph canvas
         graph_canvas <- Canvas( graph_frame, bg="grey69", bd=0)
         graph_canvas.place(x=0, y=0, height=450, width=880)
        # Key binds
        root.bind("<Key>",  keyboard_pressed)
         level_frame.bind("<Button-1>",  mouse_pressed)
        # Buy Frame
         buy_frame <- Frame( level_frame, bd=0)
         buy_frame.place(x=260 + 128 + 30 + 200, y=490 + 70, height=90, width=90)
        # Sell Frame
         sell_frame <- Frame( level_frame, bd=0)
         sell_frame.place(x=260 + 128 + 30 + 200 + 90 + 10, y=490 + 70, height=90, width=90)
        # Buy Button
         buy_button <- Button( buy_frame, bd=0, bg="lawn green", text="BUY\n\nZ", font= times_font,
                                 command=lambda:  buy())
         buy_button.place(x=0, y=0, height=90, width=90)
        # Sell Button
         sell_button <- Button( sell_frame, bd=0, bg="lawn green", text="SELL\n\nX", font= times_font,
                                  command=lambda:  sell())
         sell_button.place(x=0, y=0, height=90, width=90)
        # Restart Button
         restart_button <- Button( level_frame, bd=0, bg="lawn green", text="START\nR", font= times_font,
                                     command=lambda:  start())
         restart_button.place(x=1100, y=490 + 70, height=40, width=50)
        # Quit Button
         quit <- Button( level_frame, bd=0, text="QUIT", fg="lawn green", bg="grey10",
                           command=lambda: root.destroy())
        #  quit.config(image= power_img)
         quit.place(x=1160, y=670)
        # Timer elapsed Label
         timer_label <- Label( graph_frame, bg="grey69", text="0 seconds")
         timer_label.place(x=10, y=10, height=32, width=64)
        # Balance Label
         level_balance_label <- Label( level_frame, bg="grey10", fg="light blue", )
         level_balance_label.place(x=260 + 128 + 30 + 200, y=480, height=25, width=50)
        # Profit label
         profit_label <- Label( level_frame)
        # Stocks Counter label
         stocks_label <- Label( level_frame, bg="grey10", fg="light blue")
         stocks_label.place(x=260 + 128 + 30 + 200, y=480 + 40, height=25, width=50)
        # Current Event Textbox
         event_textbox_frame <- Frame( level_frame)
         event_textbox_frame.place(x=260 + 40, y=480, width=300, height=170)
         event_textbox <- Text( event_textbox_frame, state=DISABLED)
         event_textbox.place(x=0, y=0, width=300, height=170)
        # ListBox
         listbox <- Listbox( level_frame, bd=0, bg="grey36", fg="light blue")
         listbox.place(x=20, y=20, width=250, height=600)
         listbox.yview_moveto(0.1)
        # FPS counter
         fps_label <- Label( level_frame, bd=0, bg="grey69")
         fps_label.place(x=1100, y=22)
         fps_label.config(text="")
        # Pause Button
         pause_button <- Button( level_frame, bd=0, image= play_img, command=lambda:  pause())
         pause_button.place(x=1100, y=490, height=40, width=40)
        # Buy/Sell line
        buy_sell_line <-  graph_canvas.create_line(20, 20, 40, 40, width=2, fill="red", tags="buyLine")
    ENDFUNCTION

    FUNCTION load_all_events(self):  # loads all events from the file events.txt AND creates all of them as objects
        with open("./resources/text/events.txt") as file:
            events <- file.readlines()
        # STRIPS DATA IN FILE
        for event in events:
            evnt <- event.strip("\n").split(":")
            evnt <- Event(event_id=evnt[0], event_str=evnt[1], event_inf=evnt[2], event_des=evnt[3])
             all_events.append(evnt)
    ENDFUNCTION

        ENDFOR
    FUNCTION choose_events_for_level(self, amount):  # chooses a number of events to be embedded inside of the level
                      ENDFOR
        choiceList <- random.sample( all_events, amount)
         level_events <- choiceList
    ENDFUNCTION

    FUNCTION load_all_events_starting_ending_points(self):
        lines_amount <-  lines_amount  # the amount of lines being used in the level
        events_amount <- len( level_events)  # the amount of events being used in the level
        quart_diff <- (lines_amount / (events_amount + 1)) / 4
               ENDIF
        FOR i, num in 0 to events_amount, 1 to events_amount + 1 THEN
             level_events[i].load_start_and_end(lines_amount, events_amount, quart_diff, num)
                                                                                        ENDIF
    ENDFUNCTION

        ENDFOR
    FUNCTION create(self):  # creates a level using the basic instances, stores the level in  lines_array
        # Load AND choose events for level
                                 ENDFOR
         load_all_events()
         choose_events_for_level(amount=5)
                           ENDFOR
         load_all_events_starting_ending_points()
        for x in range( lines_amount):
            IF not  lines_array:  # IF  lines_array is empty OR equal to []
                line <- Line(lineID=x, colour= colour, startX=0, startY=225)
            ELSE:
                last <-  lines_array[-1]
                line <- Line(lineID=x, colour= colour, startX=last.endX, startY=last.endY)
            #  
            # line_count ><-
            ENDIF
            line.create_line( len_range)
            # OUTPUT line.startX,line.startY,line.endX,line.endY
             lines_array.append(line)
    ENDFUNCTION

        ENDFOR
    FUNCTION start(self):  # plays the loaded content
         running <- True
         pause(False)
        IF not  paused:
            time_start <- time.time()
            exceeded_total <- 0
            line_count <- 0
            temp_count <- 0
             graph_canvas.delete("lineTag")
             start_bal <- 500
             level_balance <-  start_bal
             level_balance_label.config(text="Balance:\n£{}".format( level_balance))
                                                                  ENDFOR
             stocks_count <- 0
             stocks_label.config(text="Stocks:\n{}".format( stocks_count))
                                                        ENDFOR
             restart_button.config(text="RESTART\nR")
             listbox.delete(0, 9999)
             line_count <- 0
             profit <- 0
             graph_boundary <- 800
            while  running:  # one cycle is one line spawned
                IF not  paused:
                    fps_start_time <- time.time()  # start time of the loop
                    elapsed <- round(time.time() - time_start)  # find time elapsed from start of start() function
                     timer_label.config(
                        text="{} seconds".format(elapsed))  # update label telling the elapsed time
                                          ENDFOR
                    try:  # checks IF the timer has been triggered
                                   ENDIF
                         stock_colour_timer_elapsed <- time.time() -  stock_colour_timer_start
                        IF  stock_colour_timer_elapsed > 1:
                             stocks_label.config(fg="light blue")
                        ENDIF
                    except:
                        pass
                    IF  lines_array[line_count].endX >=  graph_boundary:  # IF line spawned passes boundary
                         slideshow <- True
                        exceeded_current <-  lines_array[line_count].endX -  graph_boundary
                        # exceeded amount in virtual pixels past graph boundary
                         graph_boundary += exceeded_current
                        # calculate exceeded past boundary point AND implement into new graph boundary
                        exceeded_total += exceeded_current
                         graph_canvas.delete('lineTag')  # delete all lines in graph canvas
                        for y in range(line_count - 300, line_count):
                            # loops through all lines already spawned on the graph -170 in order to move them to the left
                             lines_array[y].spawn_line( graph_canvas, exceeded_total)
                    ENDIF
                        ENDFOR
                     lines_array[line_count].spawn_line( graph_canvas)  # spawn current line in x loop
                     y_pos <- ( lines_array[line_count].endY * -1) + 490
                     x_pos <-  lines_array[line_count].endX
                     current_product_price <-  y_pos
                    line_count += 1  # update index of line in lines array
                    start <- time.time()
                    while time.time() - start <  line_delay:
                        root.update()  # updates main window
                    ENDWHILE
                     fps_label.config(
                        text=f"FPS: {round((1.0 / (time.time() - fps_start_time)), 2)}")  # updates fps
                ENDIF
                root.update()  # updates main window
        ENDIF
    ENDFUNCTION

            ENDWHILE
    FUNCTION buy(self):
        IF not  paused:
            # Set Values
             buy_count += 1
             sell_count <- 0
            # Updates Balance
             level_balance -=  current_product_price
             transactions.append( level_balance)
             level_balance_label.config(text="Balance:\n£{}".format( level_balance),
                                                                  ENDFOR
                                            fg="lawn green" IF  level_balance >  start_bal else "orange red")
                                                            ENDIF
            # Updates Listbox
             listbox.insert(END, f"buy count: { buy_count} ;                             { level_balance}")
             listbox.yview(END)
            # Updates Stock Count
             stocks_count += 1
             stocks_label.config(text="Stocks:\n{}".format( stocks_count), fg="light blue")
        ENDIF
    ENDFUNCTION

                                                        ENDFOR
    FUNCTION sell(self):
        IF not  paused:
            IF  stocks_count <= 0:
                 stocks_label.config(fg="orange red")
                 stock_colour_timer_start <- time.time()
                RETURN
            ENDIF
             sell_count += 1
             buy_count <- 0
            # Updates Balance
             level_balance +=  current_product_price
             transactions.append( level_balance)
             level_balance_label.config(text="Balance:\n£{}".format( level_balance),
                                                                  ENDFOR
                                            fg="lawn green" IF  level_balance >  start_bal else "orange red")
                                                            ENDIF
            # Updates Listbox
             listbox.insert(END,
                                f"sell count: { sell_count} ;                             { level_balance}")
             listbox.yview(END)
            # Updates Profit
             profit <-  transactions[- buy_count]
            gain <- "+" IF  profit > 0 else ""
                       ENDIF
            fg <- "green2" IF  profit > 0 else "orange red"
                          ENDIF
             profit_label.config(text="{}{}".format(gain,  profit), fg=fg, bg="grey10")
                                                 ENDFOR
             profit_label.place(x=260 + 40 + 300 + 80, y=480)
            # Updates Stock Count
             stocks_count -= 1
             stocks_label.config(text="Stocks:\n{}".format( stocks_count))
        ENDIF
    ENDFUNCTION

                                                        ENDFOR
    FUNCTION keyboard_pressed(self, event):
        key <- event.keysym
        IF key = "z":
             buy()
        ELSEIF key = "x":
             sell()
        ELSEIF key = "r":
             start()
        ELSEIF key = "p":
             pause()
        ENDIF
    ENDFUNCTION

    FUNCTION mouse_pressed(self, event):
         mouse_pos <- [event.x, event.y]
        # OUTPUT  mouse_pos
    ENDFUNCTION

    FUNCTION pause(self, state=None):
        IF state is not None:
             paused <- state
        ELSEIF not  paused:  # paused status is switched on press
             pause_button.config(image= play_img)
            #  pause_button.config(image= play_img)
             paused <- True
        ELSEIF  paused:
             pause_button.config(image= pause_img)
            #  pause_button.config(image= pause_img)
             paused <- False
        ENDIF
    ENDFUNCTION

ENDCLASS

CLASS Product(Level):
    FUNCTION __init__(self, id, orgnl_prc, crrnt_prc):
         product_id <- id
         original_price <- orgnl_prc
         current_price <- crrnt_prc
         price_label <- Label()
    ENDFUNCTION

    FUNCTION display_product_name(self):
        label <- Label( level_frame, text="'product'")
        label.place()
    ENDFUNCTION

    FUNCTION database_init(self):
        cur.execute("CREATE TABLE IF NOT EXISTS Origin(player_key PRIMARY_KEY INT, password VARCHAR(16))")
        conn.commit()
    ENDFUNCTION

ENDCLASS

CLASS Line(Level):
    FUNCTION __init__(self, lineID, colour, startX=0, startY=225, endX=0,
                 endY=0):  # 225 is half of the ceiling height which is 450
         lineID <- lineID
         colour <- colour
         startX <- startX
         startY <- startY
         endX <- endX
         endY <- endY
    # create_line() happens during loading phase of the level
    ENDFUNCTION

    FUNCTION create_line(self, length_range):  # creates AND updates the line start AND end coordinates
        startX, startY <-  startX,  startY
        rand_x <- random.randint(length_range[0], length_range[1])
        rand_y <- random.randint(length_range[0], length_range[1])
        inf <- int((startY / 450) * 100)  # 450 is the height of the ceiling
        # inf <- inf *  current_event_loading.inf
        IF random.randint(0, 100) < inf:
            # % chance to flip rand_y value to negative
            rand_y *= -1
        ENDIF
        endX, endY <- startX + rand_x, startY + rand_y
        # assigns the object lines their vector positions
         startX,  startY,  endX,  endY <- startX, startY, endX, endY
    ENDFUNCTION

    FUNCTION spawn_line(self, graph_canvas, exceeded_total=0):
        graph_canvas.create_line( startX - exceeded_total,  startY,  endX - exceeded_total,  endY,
                                 width=1.5, fill= colour, tags="lineTag")
    ENDFUNCTION

ENDCLASS

CLASS Event(Level):
    FUNCTION __init__(self, event_id, event_str, event_inf, event_des):
         id <- event_id
         str <- event_str
         inf <- event_inf
         des <- event_des
         start_line <- None
         end_line <- None
    ENDFUNCTION

    FUNCTION load_start_and_end(self, lines_amount, events_amount, quart_diff, num):  # uses a formulae to calculate the duration, starting and ending point of an event
                                                                     ENDIF
                                                                                          ENDFOR
        event_number <- num
        half_line <- (lines_amount / (events_amount + 1)) * event_number
        start_line <- half_line - quart_diff
                                        ENDIF
        end_line <- half_line + quart_diff
                                      ENDIF
         start_line <- start_line
         end_line <- end_line
    ENDFUNCTION

    FUNCTION display(self):  # displays event string in textbox
        pass
    ENDFUNCTION

    FUNCTION update(self):
        pass
    ENDFUNCTION

ENDCLASS

FUNCTION open_level():
    global root, player, level
    root <- Tk()
    root.title("Stock Universe!")
    root.geometry("{}x{}".format("1200", "700"))
                          ENDFOR
    root.resizable(0, 0)
    try:
        player <- Player(username=login.username)
    except:
        player <- Player(username="developer")
    level <- Level(level_id=0, level_diff=3, line_delay=0.04, lines_amount=15000, colour="blue",
                  len_range=[3, 6])  # constructs level as an object
                                     ENDIF
    levels.append(level)
    level.create()  # creates the lines of the level
    # threadInit()
    root.mainloop()
ENDFUNCTION

FUNCTION threadInit():
    pass
ENDFUNCTION

FUNCTION open_login():
    global log_win, login
    log_win <- Tk()
    log_win.title("Login")
    log_win.geometry("{}x{}".format("600", "400"))
                             ENDFOR
    log_win.resizable(0, 0)
    login <- Login()
    log_win.mainloop()
ENDFUNCTION

IF __name__ = "__main__":
    levels <- []
    open_level()
