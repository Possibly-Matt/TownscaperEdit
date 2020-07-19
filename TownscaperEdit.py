# Townscaper Level Editor Utility
# released to the public domain by Paul Spooner
# Latest version at: http://github.com/dudecon/TownscaperEdit
# Version 1.1 2020-07-18
# Run from the save file folder
# (in Windows):
# %user\AppData\LocalLow\Oskar Stalberg\Townscaper

# Version History
# 1.2 2020-07-19 moved loading code into a function, added a menu system and a save location "picker"
#
# 1.1 2020-07-18 added filllayer(), default for save()
# 
# 1.0 2020-07-15 initial release
# included level load, save(), and functions levelcolor(), randcolor()
# buildoffset(), killrand(), hkill(),and hcull()
#



import os
from random import choice
from random import random

global infiletemplate
infiletemplate = "Town{}.scape"

global ALLCOLORS
ALLCOLORS = [i for i in range(15)]

filedata = ""



global lev_num
lev_num = -1

global num_options


def get_tag(s, tag):
    strtstr = '<{}>'.format(tag)
    endstr = '</{}>'.format(tag)
    strtpos = s.find(strtstr) + len(strtstr)
    endpos = s.find(endstr)
    tagdata = s[strtpos:endpos]
    return tagdata

def load_level(userinput):
    while True:
        #userinput = input("Load level #? ")
        try:
            lev_num = userinput
            
            infile = infiletemplate.format(lev_num)
            print("Loading:",infile)
        except:
            print("That's not a number!")
            continue
        try:
            f = open(infile,'r')
            filedata = f.read()
            f.close()
            print("Level loaded = " + str())
            print(infile, "successfully read from disc")
            break
        except:
            print("Loading ",infile," didn't work. Are you sure it exists?")
            print("Maybe you're not using the correct save directory?")
            continue
    
    coords_raw = get_tag(filedata,'corners').split('<C>')[1:]
    coords = []
    coordserial = [] #only for file loading
    voxelcount = 0
    for raw_str in coords_raw:
        newcoord = {}
        for x in ('x','y','count'): newcoord[x] = int(get_tag(raw_str, x))
        count = newcoord['count'] # recalc on save, no need to keep updated
        newcoord['vox'] = []
        coordserial += [newcoord]*count
        coords.append(newcoord)
        voxelcount += count
    del coords_raw
    voxels_raw = get_tag(filedata,'voxels').split('<V>')[1:]
    voxels = []
    voxelsin = 0
    heightmap = {}
    for raw_str in voxels_raw:
        newcoord = {}
        for x in ('t','h'): newcoord[x] = int(get_tag(raw_str, x))
        newcoord['coord'] = coordserial[voxelsin]
        coordserial[voxelsin]['vox'].append(newcoord)
        h = newcoord['h']
        if h in heightmap.keys(): heightmap[h].append(newcoord)
        else: heightmap[h] = [newcoord]
        voxelsin += 1
        voxels.append(newcoord)
    del voxels_raw
    if len(coordserial) != voxelcount: print('len(coordserial) != voxelcount')
    if len(voxels) != voxelsin: print('len(voxels) != voxelsin')
    if voxelcount != voxelsin: print('voxelcount != voxelsin')
    if len(coordserial) == voxelcount == len(voxels) == voxelsin: print(voxelsin,'voxels')
    del coordserial
    del voxelcount
    del voxelsin


def save(level_number = -1):
    global lev_num
    if level_number == -1: level_number = lev_num
    global filedata
    try:
        lev_num = int(level_number)
        outfile = infiletemplate.format(lev_num)
    except:
        print("That's not a number! Aborting")
        return False
    print("Serializing data")
    coordtemp = '''
    <C>
      <x>{}</x>
      <y>{}</y>
      <count>{}</count>
    </C>'''
    voxtemp = '''
    <V>
      <t>{}</t>
      <h>{}</h>
    </V>'''
    cornerstring = ""
    voxelstring = ""
    for coord in coords:
        count = len(coord['vox']) # recalc on save, no need to keep updated
        if count == 0: continue
        cornerstring += coordtemp.format(coord['x'],coord['y'],count)
        for vox in coord['vox']:
            t = vox['t']
            h = vox['h']
            if h < 0: h = 0
            if h > 255: h = 255
            if h == 0: t = 15 # tiny bit of error checking
            voxelstring += voxtemp.format(t,h)
    cornerstring += "\n  "
    voxelstring += "\n  "
    filedata = filedata.replace(get_tag(filedata, 'corners'),cornerstring)
    filedata = filedata.replace(get_tag(filedata, 'voxels'),voxelstring)
    print("Saving:",outfile,"with",len(voxels),"voxels")
    try:
        f = open(outfile,'w')
        f.write(filedata)
        f.close()
        print(outfile, " successfully saved to disk")
    except:
        print("Saving ",outfile," didn't work")
        return False
    return True


def levelcolor(height, color = -1):
    global heightmap
    if color == -1: color = choice(ALLCOLORS)
    for vox in heightmap[height]:
        if isinstance(color,(list,tuple)):
            thiscolor = choice(color)
        else: thiscolor = color
        vox['t'] = thiscolor
    return True

def randcolor(colors = ALLCOLORS, frac = 1):
    global voxels
    for vox in voxels:
        if random() > frac: continue
        thiscolor = choice(colors)
        vox['t'] = thiscolor
    return True

def buildoffset(basis_layer, offset = 0, frac = 0.1, color = -1):
    if color == -1: color = choice(ALLCOLORS)
    global voxels
    global heightmap
    build_height = basis_layer + offset
    if build_height > 255:
        print("built too high")
        return False
    if build_height < 0:
        print("built too low")
        return False
    for vox in heightmap[basis_layer]:
        if random() > frac: continue
        coord = vox['coord']
        alreadythere = False
        for othervox in coord['vox']:
            if othervox['h'] == build_height:
                alreadythere = othervox
                break
        if isinstance(color,(list,tuple)): thiscolor = choice(color)
        else: thiscolor = color
        if alreadythere:
            alreadythere['t'] = thiscolor
        else:
            nv = {}
            nv['coord'] = coord
            nv['t'] = thiscolor
            nv['h'] = build_height
            coord['vox'].append(nv)
            voxels.append(nv)
            if build_height in heightmap.keys():
                heightmap[build_height].append(nv)
            else: heightmap[build_height] = [nv]
    return True

def killrand(frac = 0.1):
    global voxels
    global heightmap
    for vox in voxels:
        if random() > frac: continue
        coord = vox['coord']
        del vox['coord']
        h = vox['h']
        coord['vox'].remove(vox)
        voxels.remove(vox)
        heightmap[h].remove(vox)
    return True

def hkill(height):
    global heightmap
    for vox in heightmap[height]:
        coord = vox['coord']
        del vox['coord']
        coord['vox'].remove(vox)
        voxels.remove(vox)
    del heightmap[height]
    return True

def hcull(height):
    global coords
    global voxels
    global heightmap
    for vox in heightmap[height]:
        coord = vox['coord']
        for ovox in coord['vox']:
            del ovox['coord']
            voxels.remove(ovox)
        coords.remove(coord)
    del heightmap[height]
    return True

def filllayer(height = 0, color = -1):
    if color == -1: color = choice(ALLCOLORS)
    global coords
    global voxels
    global heightmap
    if height not in heightmap.keys():
        heightmap[height] = []
    x = coords[0]['x']
    y = coords[0]['y']
    xl = x
    xs = x
    yl = y
    ys = y
    pci = {} # pre-existing coordinate index (x,y)
    for c in coords:
        x = c['x']
        y = c['y']
        xl = max(x,xl)
        xs = min(x,xs)
        yl = max(y,yl)
        ys = min(y,ys)
        pci[(x,y)] = c
    for xi in range(xs//9,1+xl//9):
        for yi in range(ys//9,1+yl//9):
            if isinstance(color,(list,tuple)): thiscolor = choice(color)
            else: thiscolor = color
            xn = xi*9
            yn = yi*9
            nv = {}
            nv['t'] = thiscolor
            nv['h'] = height
            if (xn,yn) not in pci:
                cn = {}
                cn['count'] = 0
                cn['x'] = xn
                cn['y'] = yn
                cn['vox'] = [nv]
                coords.append(cn)
                nv['coord'] = cn
                voxels.append(nv)
                heightmap[height].append(nv)
            else:
                cn = pci[(xn,yn)]
                #check for existing voxel at specified height
                voxexists = False
                for v in cn['vox']:
                    if v['h'] == height:
                        voxexists = True
                        v['t'] = thiscolor
                    if voxexists: break
                if voxexists: continue
                nv['coord'] = cn
                voxels.append(nv)
                heightmap[height].append(nv)

def yesorno(question):
    while True:
        print(question + " [y/n]")
        choice = input().lower()
        if choice == 'y':
           return True
        elif choice == 'n':
           return False
        else:
           print("Please respond with 'y' or 'n'")
           
def inputNumber(message, min = 0, max = None):
  while True:
    try:
       userInput = int(input(message))
       if isinstance(max, int): # if a max value is passed this will check if its an int, assumes minimum is 0
           if not (userInput >= 0 and userInput <= max):
                print("Between" +str(min) + " and " + str(max))
                continue
    except ValueError:
       print("Please enter a whole number. ")
       continue
    else:
       return userInput 
       break
    
num_options = 9 # this is the max number that can be selected in the menu, please update if necessary
def print_menu():
    
    print("####Menu### Loaded level: " + str(lev_num))
    print("1. Load a level")
    print("2. Save changes")
    print("3. Fill layer ")
    print("4. Recolour layer")
    print("5. Random color")
    print("6. Build Offset")
    print("7. Remove random")
    print("8. Remove layer")
    print("9. Remove all coordinates represented in a layer")
    print("0. Exit")

def is_level_loaded():
    if lev_num >= 0:
        return true
    else:
        return false
          
def menu():
    print_menu()
    menu_choice = inputNumber("", 1, num_options)
    if menu_choice == 0:
        #exit
        quit()
    elif menu_choice == 1:
        #load a level
        print("Starting level load")
        lev_num = inputNumber("Input a save number: ")        
        load_level(lev_num)
    elif menu_choice == 2:
        # save
        if is_level_loaded():
            save(lev_num)
    elif menu_choice == 3:
        # fill layer
        print()
    elif menu_choice == 4:
        # change layer colour
        print()
    elif menu_choice == 5:
        # random colour
        print()
    elif menu_choice == 6:
        # build offset
        print()
    elif menu_choice == 7:
        # remove random
        print()
    elif menu_choice == 8:
        # remove layer
        print()
    elif menu_choice == 9:
        # remove coords ?
        print()
    

# beginning 
save_dir = os.getenv("LOCALAPPDATA") + "Low\Oskar Stalberg\Townscaper" # this should be correct for most people 
correct_save_dir=yesorno("Is " + save_dir + " your save directory?")

while not correct_save_dir:
    save_dir = input("Please enter your save directory (i.e E:\...\Oskar Stalberg\Townscaper): ")
    correct_save_dir=yesorno("Is " + save_dir + " your save directory?")

os.chdir(save_dir) # sets working directory
print("Now working in save dir")
while True: # a bit uneasy about this but main() has an exit so, oh well ?
    menu()

