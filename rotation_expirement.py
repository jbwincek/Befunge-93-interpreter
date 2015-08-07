import math
    # (1,0) -> (0,-1) 
    # (0,-1) -> (-1,0) 
    # (-1,0) -> (0,1) 
    # (0,1) -> (1,0)  

def rot90(x,y):
    theta = math.pi/2 + math.pi
    nx = (x*math.cos(theta)) - (y*math.sin(theta)) 
    ny = (x*math.sin(theta)) + (y*math.cos(theta)) 
    return (int(nx),int(ny))

print(rot90(1,0))
print(rot90(0,-1))
print(rot90(-1,0))
print(rot90(0,1))