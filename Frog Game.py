import pygame,random,numpy,math
from PIL import Image
pygame.init()

SIZE = 1400, 700
SCREEN = pygame.display.set_mode(SIZE)
PATTERNS = range(1,11)

colorDic = {
    'red':(255,0,0),
    'orange':(255,175,50),
    'gold':(255,245,0),
    'citrus':(180,255,10),
    'green':(0,200,0),
    'lime':(0,255,10),
    'teal':(0,250,160),
    'aqua':(0,190,250),
    'blue':(0,50,250),
    'violet':(130,0,200),
    'purple':(200,20,250),
    'pink':(255,87,191),
    'forest':(4,100,9),
    'rorange':(139,50,10),
    'white':(250,250,252),
    'grey':(150,150,150),
    'black':(60,60,60),
    'indigo':(73,31,115),
    'steel':(71,109,125),
    'glass':(250,252,255,170),
    'electric':(0,225,255,230),
}
colorList = [i for i in colorDic]
menuList = []

def hype(x1,y1,x2,y2):
    return ((x2-x1)**2+(y2-y1)**2)**(1/2)

def within(point,lower,upper):
    if point[0]<lower[0] or point[1]<lower[1] or point[0]>upper[0] or point[1]>upper[1]: 
        return False
    return True

def makeImg(base,accent,pattern):
    base = colorDic[base]
    accent = colorDic[accent]
    patternImg = Image.open('New Game\Frog Game\patterns\{}.png'.format(pattern))
    frog = Image.alpha_composite(Image.open('New Game\Frog Game\\frg.png'), patternImg)
    jump = Image.alpha_composite(Image.open('New Game\Frog Game\\frog Jumping.png'), patternImg)
    frog, frogOld = numpy.array(frog),numpy.array(frog)
    jump, jumpOld = numpy.array(jump),numpy.array(jump)
    try: base[3]
    except: base = (base[0],base[1],base[2],255)
    try: accent[3]
    except: accent = (accent[0],accent[1],accent[2],255)
    for i in range(len(frog)):
        for j in range(len(frog[i])):
            if frogOld[i][j][3] == 255:
                if frogOld[i][j][1] > 8:
                    shade = frog[i][j][1]/255
                    frog[i][j] = (base[0]*shade,base[1]*shade,base[2]*shade,base[3])
                if frogOld[i][j][0] > 8:
                    shade = frog[i][j][0]/255
                    frog[i][j] = (accent[0]*shade,accent[1]*shade,accent[2]*shade,accent[3])
            if jumpOld[i][j][3] == 255:
                if jumpOld[i][j][1] > 8:
                    shade = jump[i][j][1]/255
                    jump[i][j] = (base[0]*shade,base[1]*shade,base[2]*shade,base[3])
                if jumpOld[i][j][0] > 8:
                    shade = jump[i][j][0]/255
                    jump[i][j] = (accent[0]*shade,accent[1]*shade,accent[2]*shade,accent[3])
    frog = Image.fromarray(frog)
    jump = Image.fromarray(jump)
    frog = pygame.image.fromstring(frog.tobytes(),frog.size,frog.mode)
    jump = pygame.image.fromstring(jump.tobytes(),jump.size,jump.mode)
    return frog, jump

class FrogClass:
    def __init__(self,colorBase,colorAccent,pattern,age, direction=random.randint(0, 360),x=random.randint(0, SIZE[0]-320),y=random.randint(0, SIZE[1]-320)):
        self.x = x
        self.y = y
        self.direction = direction
        self.colorBase = colorBase
        self.colorAccent = colorAccent
        self.pattern = pattern
        self.age = age
        self.speed = 12
        self.jumping = False
        self.jumpingto = [0,0]
        self.cooldown = random.randint(100, 600)
        self.hab = None
        self.image,self.jumpImg = makeImg(colorBase, colorAccent, pattern)
        self.width = 32*self.age
        self.height = 32*self.age
    
    def jump(self):
        self.cooldown -= 1
        if self.cooldown <= 0:
            self.jumping = True
            self.hab.removeQueue.append(self)
            while True:
                xNew, yNew = random.randint(0, 800)-400, random.randint(0, 800)-400
                self.jumpingto = (self.x - xNew,self.y-yNew)
                if within(self.jumpingto,(100,100),(SIZE[0]-100,SIZE[1]-100)): break
            self.direction = math.degrees(math.atan2(xNew,yNew))
            self.cooldown = random.randint(200, 1200)
        if self.jumping:
            ratio = self.speed/hype(self.x, self.y, self.jumpingto[0], self.jumpingto[1])
            self.x += ratio*(self.jumpingto[0]-self.x)
            self.y += ratio*(self.jumpingto[1]-self.y)
            if abs(self.x-self.jumpingto[0]) < 2*self.speed: self.jumping = False

    
    def draw(self,x,y,size,direction):
        img = self.jumpImg if self.jumping else self.image
        SCREEN.blit(pygame.transform.rotate(pygame.transform.scale(img,(32*size,32*size)),direction), (x,y))

class HabitatClass:
    def __init__(self,frogList,Background):
        self.frogList = frogList
        for i in frogList: i.hab = self
        self.Background = Background
        self.removeQueue = []
        self.type = 'habitat'
    def draw(self):
        SCREEN.blit(self.Background, (0,0))
        for i in self.frogList: 
            i.draw(i.x,i.y,i.age,i.direction)
            i.jump()
        for i in self.removeQueue:
            self.frogList.remove(i)
            self.removeQueue.remove(i)
            self.frogList.append(i)

class MenuClass:
    def __init__(self, ui, name, hab, *args, drawFrogOnStart=False):
        self.ui = ui
        self.type = 'menu'
        self.buttonList = [buttonClass(args[i][0], args[i][1], args[i][2], args[i][3], args[i][4], args[i][5], args[i][6]) for i in range(len(args))]
        self.frog = hab.frogList[0]
        self.frogSelectCoords = (400, 50, 20)
        self.name = name
        self.habitat = hab
        self.habFrogList = hab.frogList[:]
        menuList.append(self)

        if drawFrogOnStart: self.drawFrog(self.frogSelectCoords[0],self.frogSelectCoords[1],self.frogSelectCoords[2])
    
    def draw(self):
        if self.name == 'frogSelect':
            SCREEN.blit(self.ui, (0,0))
            self.drawFrog(400, 50, 20)
        for i in self.buttonList: i.draw()

    def onClick(self):
        x,y = pygame.mouse.get_pos()
        for i in self.buttonList: i.clicked(x, y)
    
    def drawFrog(self,x,y,size):
        self.frog.image, self.frog.jumpImg = makeImg(self.frog.colorBase, self.frog.colorAccent, self.frog.pattern)
        self.frog.draw(x,y,size,0)

    def action(self, action):
        if action == 'nextBase':
            self.frog.colorBase = colorList[(colorList.index(self.frog.colorBase)+1)%len(colorList)]
        elif action == 'prevBase':
            self.frog.colorBase = colorList[(colorList.index(self.frog.colorBase)-1)%len(colorList)]
        elif action == 'nextAccent':
            self.frog.colorAccent = colorList[(colorList.index(self.frog.colorAccent)+1)%len(colorList)]
        elif action == 'prevAccent':
            self.frog.colorAccent = colorList[(colorList.index(self.frog.colorAccent)-1)%len(colorList)]
        elif action == 'nextPattern':
            self.frog.pattern = PATTERNS[(PATTERNS.index(self.frog.pattern)+1)%(len(PATTERNS))]
        elif action == 'prevPattern':
            self.frog.pattern = PATTERNS[(PATTERNS.index(self.frog.pattern)-1)%(len(PATTERNS))]
        elif action == 'exit':
            global currentScreen
            currentScreen = hab1
        elif action == 'nextFrog':
            self.frog = self.habFrogList[(self.habFrogList.index(self.frog)+1)%len(self.habFrogList)]
        elif action == 'prevFrog':
            self.frog = self.habFrogList[(self.habFrogList.index(self.frog)-1)%len(self.habFrogList)]
        elif action == 'randomize':
            self.frog.colorBase = random.choice(colorList)
            self.frog.colorAccent = random.choice(colorList)
            self.frog.pattern = random.choice(PATTERNS)

        self.drawFrog(self.frogSelectCoords[0],self.frogSelectCoords[1],self.frogSelectCoords[2])
class buttonClass:
    def __init__(self,x,y,width,height,color,text,num):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.text = pygame.font.Font('freesansbold.ttf', 32).render(text, True, (255,255,255))
        self.action = num
        self.rect = pygame.rect.Rect(self.x, self.y, self.width, self.height)
    def clicked(self,x,y):
        if self.rect.collidepoint(x, y):
            menuAction(self.action)
    def draw(self):
        pygame.draw.rect(SCREEN, self.color, pygame.rect.Rect(self.x, self.y, self.width, self.height))
        SCREEN.blit(self.text, (self.x+10, self.y+10))

def menuAction(action):
    for i in menuList: i.action(action)

hab1 = HabitatClass([FrogClass(random.choice(colorList), random.choice(colorList), random.choice(PATTERNS), 5, x=random.randint(0, SIZE[0]-320),y=random.randint(0, SIZE[1]-320), direction=random.randint(0, 360)) for _ in range(20)], pygame.image.load('New Game\Frog Game\\bg1.png'))

frogSelectMenu = MenuClass(pygame.image.load('New Game\Frog Game\\bg0.png'),'frogSelect', hab1,
(50,50,200,100,(0,25,50),'Prev Base','prevBase'),
(1100,50,200,100,(0,25,50),'Next Base','nextBase'),
(50,225,220,100,(0,25,50),'Prev Accent','prevAccent'),
(1100,225,220,100,(0,25,50),'Next Accent','nextAccent'),
(50,400,220,100,(0,25,50),'Prev Pattern','prevPattern'),
(1100,400,220,100,(0,25,50),'Next Pattern','nextPattern'),
(400,550,220,100,(0,25,50),'Prev Frog','prevFrog'),
(800,550,220,100,(0,25,50),'Next Frog','nextFrog'),
(575,25,250,75,(0,50,25),'Randomize','randomize'),
(1150,610,175,75,(120,15,0),'Close','exit'),
drawFrogOnStart=True)

currentScreen = hab1

running = True
clock = pygame.time.Clock()
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT: 
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:running=False
            if event.key == pygame.K_SPACE:
                if currentScreen.type == 'menu':
                    currentScreen = hab1
                else:
                    currentScreen = frogSelectMenu
                    currentScreen.drawFrog(400, 50, 20)
        if event.type == pygame.MOUSEBUTTONUP:
            if currentScreen.type == 'menu':
                currentScreen.onClick()

    currentScreen.draw()

    clock.tick(60)
    pygame.display.update()