from math import sqrt
IPython = (__doc__ is not None) and ('IPython' in __doc__)
Main    = __name__ == '__main__'
#if IPython:
#    %gui tk
import tkinter as tk
import tkinter.ttk as ttk
from tkinter import filedialog
from time import sleep

class Vector:
    """
    A Vector is a 3-tuple of (x,y,z) coordinates.
    (int OR float, int OR float, int OR float)->Tuple
    Returns an x,y,z coordinate in a tuple.
    """
    def __init__(self,length,width,depth):
        self._x=length
        self._y=width
        self._z=depth
    
    def x(self):
        return self._x
        
    def y(self):
        return self._y
    
    def z(self):
        return self._z
    
    def __repr__(self):
        '''
        (int OR float, int OR float, int OR float)->Vector tuple
        Rounds each decimal to 3 digits, if any.
        '''
        return "(%.3g,%.3g,%.3g)" % (self._x,self._y,self._z)
        
    def norm(self):
        '''
        (Vector tuple)->float
        Take each value, squares them, adds them together, then takes the square root of the whole thing.
        Will return a positive value.
        '''
        return abs(sqrt(self._x**2 + self._y**2 + self._z**2))
    
    def __mul__(self,other):
        return Vector(self._x * other, self._y * other ,self._z * other)
    
    def __add__(self, other):
        return Vector(self._x + other._x,self._y + other._y ,self._z + other._z)
        
    def __sub__(self, other):
        return Vector(self._x - other._x,self._y - other._y ,self._z - other._z)
    
    def __eq__(self,other):
        return self._x == other._x and self._y == other._y and self._z == other._z
            
    def clear(self):
        '''
        Wipes the vector clean, sets all of x,y,z to 0.
        '''
        self._x=0
        self._y=0
        self._z=0
        return self
		
		
G = 6.67E-11

class Body:
    """
    A Body object represents the state of a celestial body.  A body has mass 
    (a scalar), position (a vector), and velocity (a vector).  A third vector, 
    named force, is used when calculating forces acting on a body.
    """
    def __init__(self,mass=0,position=Vector(0,0,0),velocity=Vector(0,0,0),force=Vector(0,0,0)):
        self._mass = mass
        self._position = position
        self._velocity = velocity
        self._force = force
    
    def mass(self):
        return self._mass
        
    def position(self):
        return self._position
    
    def velocity(self):
        return self._velocity
    
    def force(self):
        return self._force
    
    def __repr__(self):
        return "{:.3g}kg {} {}".format(self._mass,self._position,self._velocity)
        
    def direction(self, other):
        '''
        Subtracts each value in self from the corrisponding value in other. Second minus first.
        i.e.: direction((1,2,3)(3,2,1)) -> (2,0,-2) because (3-1,2-2,1-3)
        '''
        
        return Vector(other.position()._x - self.position()._x, other.position()._y - self.position()._y, other.position()._z - self.position()._z)
        
    def clear_force(self):
        '''
        Sets the force vector of a Body object to Vector(0,0,0).
        '''
        self._force=Vector(0,0,0)
        return self
    
    def add_force(self,other):
        '''
        Finds and adds the force exerted on one body by another.
        Uses the equation F=(d*M)/d^3
        F=force, d=direction, M=mass of other.
        Once the additional force has been found, it gets added to self's force vector.
        '''
        addforce= ((self.direction(other) * other._mass) * (1/(abs(self.direction(other).norm())**3)))
        
        self._force=addforce + self._force
        #return self
    
    def move(self,dt):
        '''
        Using the equation a= F*G finds the acceleration that self should have applied
        F= self's force vector, G=6.67E-11=gravitational constant
        Then adds the acceleration times dt to self's velocity. dt=time step
        Finally updates self's position by adding the new velocity times dt to self's current position.        
        '''
        a=self._force*G 
        self._velocity = self._velocity + (a * dt)
        self._position = self._position + (self._velocity * dt)
        
        return self
		
class Planet(Body):
    def __init__(self,mass=0,position=Vector(0,0,0),velocity=Vector(0,0,0),force=Vector(0,0,0),name='',color=''):
        Body.__init__(self,mass,position,velocity,force)
        self._name=name
        self._color=color
        
    def name(self):
        return self._name
    
    def color(self):
        return self._color
    
    def __eq__(self,other):
        return self._name==other
		
def step_system(bodies, dt=86459, nsteps=1):
    '''
    (list of planet/body objects, int, int) -> list of lists of tuples
    Will create the x,y coordinates for the planet/body objects as they interact over nsteps days.
    nsteps being the third argument.
    '''
    orbits=[[] for x in range(len(bodies))]
    for j in range(nsteps):
        n=0
        for p1 in bodies:
            for p2 in bodies:
                if p1 != p2:
                    p1.add_force(p2)
            p1.move(dt)
            p1.clear_force()
            orbits[n].append((p1.position().x(),p1.position().y()))
            n+=1
    return orbits
	
def read_bodies(filename, cls):
    '''
    Read descriptions of planets, return a list of body objects.  The first
    argument is the name of a file with one planet description per line, the
    second argument is the type of object to make for each planet.
    '''
    if not issubclass(cls, Body):
        raise TypeError('cls must be Body or a subclass of Body')

    bodies = [ ]

    with open(filename) as bodyfile:
        for line in bodyfile:
            line = line.strip()
            if len(line) == 0 or line[0] == '#':
                continue
            name, m, rx, ry, rz, vx, vy, vz, rad, color = line.split()
            args = {
                'mass' : float(m),
                'position' : Vector(float(rx), float(ry), float(rz)),
                'velocity' : Vector(float(vx), float(vy), float(vz)),
            }
            opts = {'name': name, 'color': color, 'size': int(rad)}
            for x in opts:
                if getattr(cls, x, None):
                    args[x] = opts[x]
            bodies.append(cls(**args))

    return bodies
	
class TkPlanet(Planet):
    def __init__(self,mass=0,position=Vector(0,0,0),velocity=Vector(0,0,0),force=Vector(0,0,0),name='',color='',size=0,graphic=None):
        Planet.__init__(self,mass,position,velocity,force,name,color)
        self._size=size
        self._graphic=graphic
    
    def size(self):
        return self._size
    
    def graphic(self):
        return self._graphic
    
    def set_graphic(self,other):
        self._graphic=other
        return None

class SolarSystemCanvas(tk.Canvas):
    
    def __init__(self, parent, height=600, width=600):
        tk.Canvas.__init__(self, parent, height=height, width=width, background='gray90', highlightthickness=0)
        self._planets = None
        self._outer = None
        self._scale = None
        self._offset = Vector(int(self['width'])/2, int(self['height'])/2, 0)
        
    def set_planets(self, lst):
        self._planets = lst
        self._outer = len(lst)
        self._compute_scale(lst)
        self.view_planets(len(lst))
        
    def view_planets(self, n):
        self._outer = n
        self.delete('all')
        self._compute_scale(self._planets[0:n])
        for i in self._planets[0:n]:
            x,y = self._compute_loc(i)
            i._graphic=self.create_oval((x-i.size(),y-i.size()),(x+i.size(),y+i.size()), fill=i.color())
        return None
        
    def move_planets(self, lst):
        for i in range(self._outer):
            x1,y1=self._current_loc(self._planets[i])
            x2,y2=self._compute_loc(lst[i])
            self.coords(lst[i]._graphic,(x2-lst[i].size(),y2-lst[i].size(),x2+lst[i].size(),y2+lst[i].size()))
            self.create_line((x1,y1),(x2,y2))
        return None
        
    def _compute_scale(self, bodies):
        self._scale=(min(tk.Canvas.winfo_height(self),tk.Canvas.winfo_width(self))/2)/(1.1*self._planets[self._outer-1].direction(self._planets[0]).norm())
        return None
    
    def _compute_loc(self, p):
        pos = p.position() * self._scale + self._offset
        return pos.x(), pos.y()
    
    def _current_loc(self, p):
        ul, ur, _, _ = self.coords(p.graphic())
        return ul + p.size(), ur + p.size()

bodies = read_bodies('solarsystem.txt', TkPlanet)		

class Viewbox(tk.Spinbox):
    
    def __init__(self, parent, callback):
        tk.Spinbox.__init__(self, parent, command=callback, width=3, state=tk.DISABLED)
                        
    def set_limit(self, nbodies=len(bodies)):
        self['state']=tk.NORMAL
        self['to']=nbodies
        self['from_']=2
        
        self.delete(0,tk.END)
        self.insert(0,str(nbodies))
        pass
		
class RunFrame(tk.Frame):
    
    def __init__(self, parent, callback):
        tk.Frame.__init__(self, parent)
        
        self['width'] = 200
        self['height'] = 100       
        
        self._run_button = tk.Button(self,text='Run',command=callback,state=tk.DISABLED)
        self._run_button.grid(row=5,column=1,padx=20,pady=10)
        
        time=tk.Label(self,text='Time step size').grid(row=0,column=0,sticky=tk.W,padx=20,pady=5)
        self._dt_entry = tk.Entry(self,text='')
        self._dt_entry.grid(row=0,column=2,pady=10)
        self._dt_entry.insert(0,'86459')
        
        steps=tk.Label(self,text='Steps to run').grid(row=1,column=0,sticky=tk.W,padx=20,pady=5)
        self._nsteps_entry = tk.Entry(self,text='')
        self._nsteps_entry.grid(row=1,column=2,pady=10)
        self._nsteps_entry.insert(0,'365')
        
        prog=tk.Label(self,text='Progress bar').grid(row=2,column=1,sticky=tk.W,padx=20,pady=5)
        self._progress= ttk.Progressbar(self, length=self['width'], maximum=self['height'])
        self._progress.grid(row=3,columnspan=3,pady=5)
        pass
        
    def dt(self):
        return int(self._dt_entry.get())
    
    def nsteps(self):
        return int(self._nsteps_entry.get())
        
    def enable_button(self):
        self._run_button['state'] = tk.NORMAL
        
    def init_progress(self, n):
        self._progress['maximum']=n
        pass
        
    def update_progress(self, n):
        self._progress['value'] += n
        pass
        
    def clear_progress(self):
        self._progress['value'] = 0

root = tk.Tk()
root.title("Solar System")

bodies = None

def load_cb():
    global bodies
    fn = tk.filedialog.askopenfilename()
    bodies = read_bodies(fn, TkPlanet)
    canvas.set_planets(bodies)
    view_counter.set_limit(len(bodies))
    run_frame.enable_button()

def view_cb():
    canvas.view_planets(int(view_counter.get()))
    
def run_cb():
    
    def time_step():
        nonlocal nsteps
        step_system(bodies, dt)
        canvas.move_planets(bodies)
        run_frame.update_progress(1)
        sleep(0.02)
        if nsteps > 0:
            nsteps -= 1
            canvas.after_idle(time_step)
        else:
            run_frame.clear_progress()
        
    nsteps = run_frame.nsteps()
    run_frame.init_progress(nsteps)
    dt = run_frame.dt()
    canvas.after_idle(time_step)

canvas = SolarSystemCanvas(root)
canvas.grid(row = 0, column = 0, columnspan = 3, padx = 10, pady = 10, sticky="nsew")

tk.Button(root, text='Load', command=load_cb).grid(row=1, column=0, pady = 20)

view_frame = tk.Frame(root, width=100)
tk.Label(view_frame, text='Planets to View').pack()
view_counter = Viewbox(view_frame, view_cb)
view_counter.pack()
view_frame.grid(row=1, column=1, pady=20)

run_frame = RunFrame(root, run_cb)
run_frame.grid(row=1, column=2, pady=20)

if Main and not IPython:
    try:
        bodies = read_bodies("solarsystem.txt", TkPlanet)
        canvas.set_planets(bodies)
        view_count.reset(len(bodies))
        for i in range(5):
            view_count._spinbox.invoke('buttondown')
        run_frame._nsteps_entry.delete(0, tk.END)
        run_frame._nsteps_entry.insert(0,'100')
        root.update()
        run_frame._run_button.invoke()
    except Exception as err:
        print(err)
    input('hit return to continue...')
