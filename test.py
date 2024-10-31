import tkinter as tk

root = tk.Tk()
canvas = tk.Canvas(root)
canvas.pack()
item = canvas.create_rectangle(50, 25, 150, 75, fill="blue")
item1 = canvas.create_rectangle(50, 25, 150, 75, fill="blue")
item2 = canvas.create_rectangle(50, 25, 150, 75, fill="blue")
item3 = canvas.create_rectangle(50, 25, 150, 75, fill="blue")
item4 = canvas.create_rectangle(50, 25, 150, 75, fill="blue")
item5 = canvas.create_line(50, 25, 150, 75, fill="red")
print(item)

def callback():
    canvas.itemconfig(item,fill='red')

button = tk.Button(root,text='Push me!',command=callback)
button.pack()

root.mainloop()