'''
class NameofClass():    #назва класу
    def __init__(self,param1, param2):   #init - метод дозволяє створити екземпляв реального класу
                                         #param1, param2 - attribute
                                         #self - використовується аби пайтон розумів шо це метод який підключений до цього класу
        self.param1 = param1
        self.param2 = param2
'''

'''
Attributes
The syntax for creating an attribute is:

self.attribute = something
There is a special method called:

init()

This method is used to initialize the attributes of an object.For example:

class Dog:
    def init(self, breed):
        self.breed = breed


sam = Dog(breed='Lab')
frank = Dog(breed='Huskie')
'''


class Circle:
    pi = 3.14

    # Circle gets instantiated with a radius (default is 1)
    def __init__(self, radius=1):
        self.radius = radius
        self.area = radius * radius * Circle.pi     # or self.pi   ??

    # Method for resetting Radius
    def setRadius(self, new_radius):
        self.radius = new_radius
        self.area = new_radius * new_radius * self.pi

    # Method for getting Circumference
    def getCircumference(self):
        return self.radius * self.pi * 2


c = Circle()

print('Radius is: ',c.radius)
print('Area is: ',c.area)
print('Circumference is: ',c.getCircumference())

# Inheritance

class Animal:
    def __init__(self):
        print("Animal created")

    def whoAmI(self):
        print("Animal")

    def eat(self):
        print("Eating")


class Dog(Animal):
    def __init__(self):
        Animal.__init__(self)
        print("Dog created")

    def whoAmI(self):
        print("Dog")

    def bark(self):
        print("Woof!")


# Polymorphism

class Dog:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return self.name + ' says Woof!'


class Cat:
    def __init__(self, name):
        self.name = name

    def speak(self):
        return self.name + ' says Meow!'


niko = Dog('Niko')
felix = Cat('Felix')