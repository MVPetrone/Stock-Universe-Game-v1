from tkinter import *
root = Tk()
root.geometry("500x500")


canvas = Canvas(root, height=400, width=500)
canvas.pack()

canvas.create_line(100, 10, 300, 300, width=4, fill="red", tag="red_line")
canvas.create_line(60, 60, 380, 20, width=4, fill="black", tag="line")
canvas.create_line(60+20, 60, 380, 20, width=4, fill="black", tag="line")
canvas.create_line(60+30, 60, 380, 20, width=4, fill="black", tag="line")
canvas.create_line(60+40, 60, 380, 20, width=4, fill="black", tag="line")
canvas.create_line(60+50, 60, 380, 20, width=4, fill="black", tag="line")
canvas.create_line(60+60, 60, 380, 20, width=4, fill="black", tag="line")
canvas.create_line(60+70, 60, 380, 20, width=4, fill="black", tag="line")
canvas.create_line(60+80, 60, 380, 20, width=4, fill="black", tag="line")
canvas.create_line(60+90, 60, 380, 20, width=4, fill="black", tag="line")
canvas.create_line(60+100, 60, 380, 20, width=4, fill="black", tag="line")

button_clear = Button(root, text="Clear", command=lambda: canvas.delete("line"))
button_clear.pack()

button_move = Button(root, text="Move", command=lambda: canvas.move("red_line", 40, 100))
button_move.pack()


root.mainloop()