from tkinter import *

window = Tk()
photo = PhotoImage(file=r"C:\Users\maxib\Documents\python stuff\pythontowerdefense\exit.png")
window.title("my window")
window.config(background="black")


def click():
    print("you clicked the button")


label = Label(
    window,
    text="i goon",
    font=("Arial", 40, "bold"),
    fg="#ff9cae",
    bg="white",
    relief=RAISED,
    bd=10,
    padx=20,
    pady=10,
    image=photo,
    compound="left",
)
label.pack()

button = Button(
    window,
    text="click me to goon",
    font=("Comic Sans", 60, "italic"),
    fg="#fe9fff",
    bg="white",
    foreground="#fe9fff",
    command=click,
)
button.pack()

window.mainloop()