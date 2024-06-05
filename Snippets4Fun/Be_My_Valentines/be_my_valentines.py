import turtle

# Create the turtle pen
pen = turtle.Turtle()

# Set the speed of the turtle to the maximum (0)
pen.speed(0)

def curve():
    # Reduce the number of iterations by increasing the forward step
    for i in range(100):
        pen.right(2)
        pen.forward(2)

def heart():
    pen.fillcolor('red')
    pen.begin_fill()
    pen.left(140)
    pen.forward(113)
    curve()
    pen.left(120)
    curve()
    pen.forward(112)
    pen.end_fill()  # Added end_fill() to properly close the filled shape

def text1():
    pen.up()
    pen.setpos(-68, 95)
    pen.down()
    pen.color('blue')
    pen.write("i luv it", font=("Arial", 16, "bold"))

heart()
text1()
pen.ht()  # Hide the turtle
turtle.done()
