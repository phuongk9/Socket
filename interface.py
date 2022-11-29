import tkinter as tk
from PIL import Image,ImageTk
root= tk.Tk()
WIDTH  = 1270
HEIGHT = 760

img = Image.open("background.png")
resize_image = img.resize((WIDTH,HEIGHT))
image= ImageTk.PhotoImage(resize_image)

canvas1 = tk.Canvas(root, width=WIDTH, height=HEIGHT, relief='raised')
canvas1.pack(fill = "both", expand = True)
background = tk.Label(image=image)
background.place(x=0,y=0)
    


entry1 = tk.Entry(root,width=20, font=('helvetica',35))
canvas1.create_window(WIDTH/2,150, window=entry1)
def download():
    url = entry1.get()
    label2 = tk.Label(root, text=url,bg='black',fg='white',font=('helvetica',25))
    canvas1.create_window(WIDTH/2,450,window=label2)
button1 = tk.Button(text="Download", command=download,bg='#ffc107',font=('helvetica',35,'bold'))
canvas1.create_window(WIDTH/2,300,window=button1) 
root.mainloop()
