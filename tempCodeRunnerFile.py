import tkinter as tk

root= tk.Tk()
WIDTH  = 1270
HEIGHT = 760
canvas1 = tk.Canvas(root, width=WIDTH, height=HEIGHT, relief='raised', bg='black')
canvas1.pack()

label1 = tk.Label(root, text='Type your URL',bg='black',fg='white')
label1.config(font=('helvetica', 35))
canvas1.create_window(WIDTH/2,200, window=label1)

entry1 = tk.Entry(root,width=10, font=('helvetica',35))
canvas1.create_window(WIDTH/2,300, window=entry1)
def download():
    url = entry1.get()
    label2 = tk.Label(root, text=url,bg='black',fg='white',font=('helvetica',35))
    canvas1.create_window(WIDTH/2,500,window=label2)
button1 = tk.Button(text="Download", command=download,bg='yellow',font=('helvetica',35,'bold'))
canvas1.create_window(WIDTH/2,400,window=button1)
root.mainloop()
