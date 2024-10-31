class Database:

    def __init__(self, sqlite3):

        self.sqlite3 = sqlite3

        self.conn = None
        self.cur = None

    def connect(self, path=None):

        if path is None:
            raise Exception("path cant be none")

        self.conn = self.sqlite3.connect(path)  # connects to database
        self.cur = self.conn.cursor()

    def create_accounts_table(self):

        self.connect("./databases/logins.db")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS Accounts(
                            username VARCHAR(16), 
                            password VARCHAR(16), 
                            player_key INT
                            )""")
        self.conn.commit()

    def create_playerdata_table(self):

        self.connect("./databases/logins.db")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS PlayerData(
                            player_key PRIMARY_KEY INT,
                            xp_level INT,
                            xp INT, 
                            levels_unlocked INT, 
                            products_unlocked INT, 
                            balance INT, 
                            capacity INT
                            )""")
        self.conn.commit()

    def create_origin_table(self):

        self.connect("./databases/products.db")

        self.cur.execute("""CREATE TABLE IF NOT EXISTS Origin(
                            id PRIMARY_KEY INT, 
                            name VARCHAR(16), 
                            value FLOAT, 
                            difficulty VARCHAR(16), 
                            vol_rate FLOAT
                            )""")
        self.conn.commit()

    def create_gem_table(self):

        pass

    def create_decay_table(self):

        pass
