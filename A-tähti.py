import pygame, time

class Settings:
    tileColor = (150,150,150)
    menuColor = (150,150,150)
    menuTextColor= (35,25,25)
    goalColor = (150,100,100)
    startColor= (100,150,100)
    obstacleColor= (50,50,50)
    closedColor=(150,100,100)
    openColor = (100,150,100)
    pathColor = (100,100,150)
    tileFont = "Lucida Bright"
    menuFont = "Lucida Bright"

class Tile:
    def __init__(self):
        self.gscore = 9900 #Distance from start
        self.hscore = 9900 #Distance from end
        self.fscore = 0       #Total of the two
        self.isObstacle = False
        self.cameFrom = None
        self.formsPath = False
        self.x = None
        self.y = None
    def __repr__(self):
        return f"{self.x},{self.y}"

class Astar:
    def __init__(self, start, goal, tiles):
        self.open = set() # Tiles to check
        self.closed = set() # Tiles already checked
        self.allTiles = tiles
        self.open.add(start)
        self.goal = goal
        self.allowDiagonal = True
        self.hasFinished = False

        start.gscore = 0
        start.hscore = self.heuristicScore(start)
        start.fscore = start.hscore + start.gscore
    
    def run(self):
        """Runs one cycle of the algorithm"""
        if self.hasFinished:
            return 1
        if len(self.open) <= 0:
            self.hasFinished = True
            print("No possible paths")
            return 1
        # Tile with the lowest Fscore
        current = min(self.open, key=lambda item: item.fscore + 0.01 * item.hscore)
        self.open.remove(current)
        self.closed.add(current)
        if current == self.goal:
            print("Hit goal")
            self.hasFinished = True
            while current.cameFrom != None: # Reconstruct path
                current.formsPath = True
                current = current.cameFrom
            return 1
        for neighbour, gscoreChange in self.getNeighbours(current):
            if neighbour.isObstacle == True:
                continue
            if neighbour in self.closed:
                continue
            if current.gscore + gscoreChange < neighbour.gscore or neighbour not in self.open:
                # Do stuff to neighbour
                neighbour.hscore = self.heuristicScore(neighbour)
                neighbour.gscore = current.gscore + gscoreChange
                neighbour.fscore = neighbour.hscore + neighbour.gscore
                neighbour.cameFrom = current
                if neighbour not in self.open:
                    self.open.add(neighbour)

    def getNeighbours(self, tile):
        """Returns a tuple (tile, fscore_to) for every adjecant tile"""
        neighbours = []
        for spot in (-1,0), (0,-1), (1,0), (0,1):
            if tile.x + spot[0] < 0 or tile.x + spot[0] >= len(self.allTiles[0]):
                # Off grid X
                continue
            if tile.y + spot[1] < 0 or tile.y + spot[1] >= len(self.allTiles):
                # Off grid Y
                continue
            # Add tile with the said offset to the neighbours with the fscore
            neighbours.append((self.allTiles[tile.y + spot[1]][tile.x + spot[0]],10))
        if self.allowDiagonal:
            for spot in (-1,-1), (1,-1), (1,1), (-1,1):
                if tile.x + spot[0] < 0 or tile.x + spot[0] >= len(self.allTiles[0]):
                    # Off grid X
                    continue
                if tile.y + spot[1] < 0 or tile.y + spot[1] >= len(self.allTiles):
                    # Off grid Y
                    continue
                # Add tile with the said offset to the neighbours with the fscore
                neighbours.append((self.allTiles[tile.y + spot[1]][tile.x + spot[0]],14))
        return neighbours

    def heuristicScore(self, tile):
        """Returns heuristic score for any tile (distance from goal) (diagonal is 14 points)"""
        dx = abs(self.goal.x - tile.x)
        dy = abs(self.goal.y - tile.y)
        return (dx + dy) * 10 - min(dx,dy) * 6


class App:
    """App that controls and displays Astar"""
    def __init__(self):
        pygame.init()
        self.screenSize = (500,500)
        self.screen = pygame.display.set_mode(self.screenSize, pygame.RESIZABLE)
        self.tilesize = 30 # Size of the tile in pixels (x and y)
        self.tileCount = self.getTileCount(self.screenSize)
        self.generateTiles()
        self.start = self.tiles[0][0]
        self.goal = self.tiles[0][5]
        self.stop = False # Setting to true will stop the application
        self.pathfinder = None # Stores Astar class when pathfinding is started
        self.runMode = "automatic" # Enums would be better
        self.lastAutomaticRun = 0
        self.buttonHeld = False
        # Fonts
        self.tileFontObject = pygame.font.SysFont(Settings.tileFont, 8)
        self.menuFontObject = pygame.font.SysFont(Settings.menuFont, 16)
        # Start
        self.main()

    def main(self):
        """Main loop of the App class. Calls event functions"""
        while not self.stop:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.stop = True
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    x,y = event.pos
                    gridx, gridy = int(x/self.tilesize), int((y-30)/self.tilesize)
                    if event.button == 1: # Left click
                        if self.tiles[gridy][gridx].isObstacle:
                            self.buttonHeld = 2 # remove tiles when dragged
                        else:
                            self.buttonHeld = 1 # add tiles when dragged
                    if y > 31:
                        if self.pathfinder == None:
                            self.gridClick(gridx, gridy, event.button)
                        else:
                            # Pathfinder is set, no editing
                            self.animationClick()
                    else:
                        # menu bar
                        if x < 100:
                            # clicked on the Run button
                            self.buttonRun()
                        elif x < 200:
                            self.buttonStyle()
                elif event.type == pygame.VIDEORESIZE:
                    self.resize(event.size)
                elif event.type == pygame.MOUSEMOTION:
                    if self.buttonHeld == 0: continue
                    x, y = event.pos
                    gridx, gridy = int(x/self.tilesize), int((y-30)/self.tilesize)
                    if y > 31:
                        if self.pathfinder == None:
                            self.drag(gridx, gridy)
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.buttonHeld = 0
            if not self.buttonHeld:
                time.sleep(0.05) # Normal frametime
            else:
                time.sleep(0.01) # Higher framerate for smoother drawing
            if self.pathfinder != None and self.runMode == "automatic":
                self.lastAutomaticRun -= 1 # Runs every 3 (frames) 0.15 seconds with sleep time of 0.05
                if self.lastAutomaticRun < 0:
                    self.pathfinder.run()
                    self.lastAutomaticRun = 3
                    self.draw()
    
    def draw(self):
        """Draws the enitere screen, when editing. (pathfinder is inactive)"""
        self.screen.fill((50,50,50)) # Fill grey
        # Draw menu
            # Run/stop
        pygame.draw.rect(self.screen, Settings.menuColor, (1,1,100,29))
        if self.pathfinder == None:
            buttontxt = "Start"
        else:
            buttontxt = "Stop"
        textsurface = self.menuFontObject.render(buttontxt, True, Settings.menuTextColor)
        self.screen.blit(textsurface,(6,6))
            # Run style
        pygame.draw.rect(self.screen, Settings.menuColor, (102,1,100,29))
        textsurface = self.menuFontObject.render(self.runMode.capitalize(), True, Settings.menuTextColor)
        self.screen.blit(textsurface,(106,6))
        # Draw grid
        self.drawGrid()
        pygame.display.update()
    
    def drawGrid(self):
        """Seperated from Draw main function. Draws grid of the application in edit & run modes"""
        if self.pathfinder == None: # In edit mode
            for y in range(self.tileCount[1]):
                for x in range(self.tileCount[0]):
                    tile = self.tiles[y][x]
                    if tile.isObstacle:
                        tilecolor = Settings.obstacleColor
                    elif tile is self.goal:
                        tilecolor = Settings.goalColor
                    elif tile is self.start:
                        tilecolor = Settings.startColor
                    else:
                        tilecolor = Settings.tileColor
                    pygame.draw.rect(self.screen, tilecolor, (1 + x*self.tilesize, 31 + y*self.tilesize, self.tilesize-1, self.tilesize-1))
                    #textsurface = self.tileFontObject.render(".",True,(0,0,0))
                    #self.screen.blit(textsurface, (x * self.tilesize + 4, y * self.tilesize + 34))
        else: # In run mode
            for y in range(self.tileCount[1]):
                for x in range(self.tileCount[0]):
                    tile = self.tiles[y][x]
                    drawText = True
                    if tile.isObstacle:
                        tilecolor = Settings.obstacleColor
                        drawText = False
                    elif tile is self.goal or tile is self.start or tile.formsPath:
                        tilecolor = Settings.pathColor
                    elif tile in self.pathfinder.closed:
                        tilecolor = Settings.closedColor
                    elif tile in self.pathfinder.open:
                        tilecolor = Settings.openColor
                    else:
                        tilecolor = Settings.tileColor
                        drawText = False
                    pygame.draw.rect(self.screen, tilecolor, (1 + x*self.tilesize, 31 + y*self.tilesize, self.tilesize-1, self.tilesize-1))
                    if drawText:
                        # F
                        textsurface = self.tileFontObject.render("{:3}".format(tile.fscore),True,(0,0,0))
                        self.screen.blit(textsurface, (x * self.tilesize + 4, y * self.tilesize + 31))
                        # H + G
                        hgtext = "{:2} {:2}".format(tile.hscore,tile.gscore)
                        textsurface = self.tileFontObject.render("{:^7}".format(hgtext),True,(0,0,0))
                        self.screen.blit(textsurface, (x * self.tilesize, y * self.tilesize + 47))

    def getTileCount(self, size):
        """Gets the number of tiles that can fit in the screen size"""
        screenx = size[0] - 1
        screeny = size[1] - 31
        return int(screenx/self.tilesize), int(screeny/self.tilesize)

    def resize(self, size):
        """Function that is called whenever the user resizes the app window.
        :param size: tuple"""
        self.screenSize = size
        self.screen = pygame.display.set_mode(self.screenSize, pygame.RESIZABLE)
        self.tileCount = self.getTileCount(size)
        self.generateTiles(self.tiles)
        self.draw()
    
    def generateTiles(self, oldtiles = None):
        """Generates the tiles on app start and adds more tiles if needed on resize"""
        self.tiles = []
        xlen,ylen = self.tileCount
        for y in range(ylen):
            line = []
            for x in range(xlen):
                if oldtiles != None:
                    try:
                        add = oldtiles[y][x]
                    except IndexError:
                        add = Tile()
                else:
                    add = Tile()
                add.x = x
                add.y = y
                line.append(add)
            self.tiles.append(line)
        #print(xlen, ylen)
        #print(self.tiles)
    
    def gridClick(self,x,y,button):
        """Does stuff to whatever grid postion you clicked at"""
        if x >= self.tileCount[0] or y >= self.tileCount[1]:
            return
        tile = self.tiles[y][x]
        if button == 1: #left click
            if tile is self.goal or tile is self.start:
                return
            tile.isObstacle = not tile.isObstacle
            self.draw()
        elif button == 3: #right click
            if tile.isObstacle:
                return
            if tile is self.goal:
                self.goal = None
            elif tile is self.start:
                self.start = None
            elif self.start == None:
                self.start = tile
            elif self.goal == None:
                self.goal = tile
            self.draw()
    
    def drag(self, x, y):
        """Places or removes obstacles when dragging"""
        if self.buttonHeld == 1:
            makeObstacle = True
        else:
            makeObstacle = False
        if x >= self.tileCount[0] or y >= self.tileCount[1]:
            return
        tile = self.tiles[y][x]
        if tile is self.goal or tile is self.start:
            return
        tile.isObstacle = makeObstacle
        self.draw()

    def buttonRun(self):
        """Code for run button, supposed to start pathfinding"""
        if self.pathfinder == None:
            if self.start == None:
                print("You need to select a starting point by right clicking")
                return
            if self.goal == None:
                print("You need to select ending point by right clicking")
                return
            self.clearTileData()
            self.pathfinder = Astar(self.start, self.goal, self.tiles)
            if self.runMode == "instant":
                self.instantComplete()
            self.draw()
        else:
            self.pathfinder = None
            self.draw()

    def buttonStyle(self):
        """Second in app button for changing run style"""
        styles = ("click","automatic","instant")
        i = styles.index(self.runMode)
        self.runMode = styles[(i + 1) % len(styles)]
        # If pathfinder is running and instant is selected, complete the pathfind
        if self.runMode == "instant" and self.pathfinder != None:
            self.instantComplete()
        self.draw()
    
    def instantComplete(self):
        """Run instant complete on pathfinder"""
        for x in range(10**3):
            val = self.pathfinder.run()
            if val == 1:
                break
        else: #Nobreak
            print("No path found in 1000 attempts")

    def animationClick(self):
        """Code that runs when screen is clicked while there is a pathfinder active (pathfinder moves by a frame)"""
        self.pathfinder.run()
        self.draw()
                
    def clearTileData(self):
        for y in range(self.tileCount[1]):
            for x in range(self.tileCount[0]):
                self.tiles[y][x].formsPath = False

if __name__ == "__main__":
    App()
