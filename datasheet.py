class Datasheet:

    def __init__(self, root, tk):

        self.root = root

        self.frame = tk.Frame(root)
        self.showing = False

    def show(self):

        if not self.showing:
            self.showing = True
            self.frame.place(x=20, y=20, height=200, width=300)

        else:
            self.showing = False
            self.frame.place_forget()