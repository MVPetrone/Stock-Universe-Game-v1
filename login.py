class Login:

    def __init__(self, database, tk):

        self.log_win = tk.Tk()

        self.log_win.title("Login")
        self.log_win.geometry("{}x{}".format("600", "400"))
        self.log_win.resizable(0, 0)
        self.log_win.iconbitmap("./resources/textures/icon2.ico")

        self.database = database

        self.login_successful = False
        self.login_status = "Not Logged In"

        self.frame = tk.Frame(self.log_win, bg="lavender")
        self.frame.place(x=0, y=0, height=400, width=600)
        self.check_entries_button = tk.Button(self.frame, bd=1, command=lambda: self.check_entries())
        self.register_button = tk.Button(self.frame, text="REGISTER", bd=0, bg="firebrick1",
                                      command=lambda: self.register())
        self.login_button = tk.Button(self.frame, text="LOGIN", bd=0, bg="firebrick1", command=lambda: self.login())
        self.u_entry = tk.Entry(self.frame, text="Enter username")
        self.p_entry = tk.Entry(self.frame, text="Enter password", show="•")
        self.back_button = tk.Button(self.frame, text="<-", command=lambda: self.main_menu(), bd=1)
        self.status_label = tk.Label(self.frame, text=self.login_status, bg="lavender")
        self.status_label.place(x=200, y=20)
        self.play_button = tk.Button(self.frame, text="PLAY GAME", bd=0, bg="firebrick1", command=lambda: self.play())
        self.play_button.place(x=200, y=100 + 60 + 10 + 60 + 10, height=60, width=200)
        self.main_menu()

        self.log_win.mainloop()

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
        self.check_entries_button.place(x=300 - 50, y=230, height=20, width=100)
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
        self.check_entries_button.place(x=300 - 50, y=230, height=20, width=100)
        self.register_button.place_forget()
        self.login_button.place_forget()
        self.u_entry.place(x=200, y=100, height=30, width=200)
        self.p_entry.place(x=200, y=100 + 50, height=30, width=200)

    def exists(self, username):

        # CHECKS TO SEE IF USERNAME EXISTS IN DATABASE RETURNING TRUE OR FALSE

        self.database.connect("./databases/logins.db")

        self.database.cur.execute("SELECT username FROM Accounts")  # gets all usernames in database
        usernames = []
        for x in self.database.cur.fetchall():
            usernames.append(x[0])

        for x in usernames:
            if x == username:
                self.database.conn.close()
                return True
        return False

    def check_entries(self):

        # RETRIEVES ENTRY DATA AND COMPARES TO DATABASE

        self.database.create_accounts_table()
        self.database.create_playerdata_table()

        u_input = self.u_entry.get()
        p_input = self.p_entry.get()

        if self.state == "register":

            if not (3 <= len(u_input) <= 16):
                self.status_label.config(text="Username must be between 3 and 16 characters", fg="red")
                # self.flash_red(self.status_label)

            elif self.exists(u_input):
                self.status_label.config(text="Username already exists", fg="red")
                # self.flash_red(self.status_label)

            else:
                player_keys = []
                self.database.connect("./databases/logins.db")
                self.database.cur.execute("SELECT player_key FROM Accounts")  # gets all usernames in database
                for x in self.database.cur.fetchall():
                    player_keys.append(x[0])
                player_key = len(player_keys)

                self.database.cur.execute("INSERT INTO Accounts(username,password,player_key) VALUES(?,?,?)",
                                     (u_input, p_input, player_key))
                self.database.conn.commit()

                self.database.cur.execute("""INSERT INTO PlayerData(player_key, xp_level, xp, levels_unlocked, 
                                        products_unlocked, balance, capacity) VALUES(?,?,?,?,?,?,?)""",
                                     (player_key, 0, 0, 1, 1, 500, 10))
                self.database.conn.commit()

                self.status_label.config(text="Account Registered", fg="black")

                self.u_entry.delete(0, 999)
                self.p_entry.delete(0, 999)

        elif self.state == "login":

            self.u_entry.delete(0, 999)
            self.p_entry.delete(0, 999)

            self.database.cur.execute("SELECT username FROM Accounts")  # gets all usernames in database
            usernames = []
            for x in self.database.cur.fetchall():
                usernames.append(x[0])

            self.database.cur.execute("SELECT password FROM Accounts")  # gets all passwords in database
            passwords = []
            for x in self.database.cur.fetchall():
                passwords.append(x[0])

            self.database.cur.execute("SELECT player_key FROM Accounts")  # gets all passwords in database
            player_keys = []
            for x in self.database.cur.fetchall():
                player_keys.append(x[0])

            # CHECKS IF USERNAME AND PASSWORD INDEX ARE THE SAME WITH THE DATABASE

            for i in range(len(usernames)):
                if u_input == usernames[i]:
                    if p_input == passwords[i]:
                        self.username = usernames[i]
                        self.password = passwords[i]
                        self.player_key = player_keys[i]
                        self.login_successful = True
                        self.login_status = "Logged in as: {}".format(self.username)
                        self.status_label.config(text=self.login_status, fg="black")
                        break

            if not self.login_successful:  # if username does not match password
                self.status_label.config(text="Incorrect username or password", fg="red")

        self.database.conn.close()

    def play(self):

        if self.login_successful:
            self.log_win.destroy()

        else:
            self.status_label.config(text="Must be logged in to play", fg="red")
