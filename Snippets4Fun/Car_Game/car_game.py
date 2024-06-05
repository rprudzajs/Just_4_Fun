##Remeber to install Ursina in your environment. pip install ursina

from ursina import *

app = Ursina()

camera.orthographic = True
camera.fov = 10

car = Entity(
    model='quad',
    texture='cartop.png',  #Here you select your car file name (must be in same folder)
    collider='box',
    scale=(2, 1),
    x=3
)

road1 = Entity(
    model='quad',
    texture='highway.png', #Here you select your highway file name
    scale=15,
    z=1
)

road2 = duplicate(road1, y=15)
pair = [road1, road2]

enemies = []
import random
def newEnemy():
    val = random.uniform(-2,2)
    new = duplicate(
        car,
        texture = 'no_title',   ##If you want an especific image for an enemy, replace this with the file name.
        x = 2*val,               ##If not, just leave it like that and will duplicate from our car file
        y= 25,
        color=color.random_color(), ##We select the specific color of your enemy
        
    )
    enemies.append(new)
    invoke(newEnemy, delay=0.5)
newEnemy()

def update():
    car.x -= held_keys['a'] * 5 * time.dt
    car.x += held_keys['d'] * 5 * time.dt
    for road in pair:
        road.y -= 6 * time.dt
        if road.y < -15:
            road.y += 30
    for enemy in enemies:
        if enemy.x < 0:
            enemy.y -= 10 * time.dt
        else:
            enemy.y -=5 * time.dt
app.run()

