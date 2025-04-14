import pygame
import random
import threading 
import time
import random

###################Plant_Simulation V_0.2#########################################
###########Todo Liste#######################################
# 7. Mutationen vllt einbauen
# 10. Geschwindigkeit einfach anpassbar -> Config Datei
# 11. UI verbessern -> Graphen, Komplizierter: Pflanze anklicken und dann öffnet sich ein seperates Fenster mit infos über die Pflanze 
# 12. Regenanimation (Einzelne random Pixel die sich Bläuchlich färben)
# -> Wichtig Plfanzenschäden sollten auch wieder weg gehen wenn die Pflanze sich regeneriert hat ######### !!! Wichtig !!!! #########
###################################################################
######################Schönheit#####################################
# 2.  
######################Ganz Späte Ideen##############################
# 1. Stammbaum
# 2. Logisch generierte Pflanzennamen                                                                                     ###### So halb fertig
# 4. Größeren Bildschirm für Raspi kaufen und darauf das laufen lassen auch als schöne und interesannte Deko              ###### Echt gute Idee

############################################################
#####################Bug Liste################################




############################################################

# Fenstergröße und Gittereinstellungen
GRID_SIZE = 30  
GRID_WIDTH = 26  
GRID_HEIGHT = 20  
WIDTH, HEIGHT = GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE  
INFO_WIDTH = 300
INFO_HEIGHT = 200

# Farben
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GRAY = (200, 200, 200)
BLACK = (0, 0, 0)
BLUE =  (0, 0, 255)
DARKBLUE = (0, 0, 128)
DARKGREEN = (28, 87, 4)


pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Pflanzen Simulation")
clock = pygame.time.Clock()

############################################################
# Pflanzennamen
with open("Pflanzennamen.txt", "r", encoding="utf-8") as file:
    namen = file.readlines()

# Nachkommennamen Generieren
def Nachnamengenerieren(parent):
    suffix_count = 1
    current_parent = parent
    while current_parent.Eltern:
        if current_parent.Pflanzenname.split()[0] == parent.Pflanzenname.split()[0]:
            suffix_count += 1
        current_parent = current_parent.Eltern
    return " " + "I" * suffix_count  # Beispiel: "Eichenbaum II"

initial_name_counter = 0
# Lebewesen-Klasse
class Creature:
    def __init__(self, x, y, eltern=None):
        global initial_name_counter

        self.x = x
        self.y = y
        self.Energie = 100  
        self.Alter = 0      
        self.Wachstumsstadium = "Setzling"  
        self.Eltern = eltern  
        self.Mutationen = []
        # Mutationsfaktoren
        self.Wasserverbrauch = 5
        self.Nahrungsverbrauch = 5
        self.Energieverbrauch = 4
        #Wetterschäden : Ast abgebrochen, Frostschaden, Hagelschaden, Infektion
        self.Wetterschäden = []


        # Namensvergabe
        if initial_name_counter < 10:
            self.Pflanzenname = random.choice(namen).strip()
            initial_name_counter += 1
        else:
            if eltern:
                self.Pflanzenname = f"{eltern.Pflanzenname.split()[0]}{Nachnamengenerieren(eltern)}"
            else:
                self.Pflanzenname = "Unbekannte Pflanze"

    def draw(self, surface):
        if self.Wachstumsstadium == "Setzling":
            Setzling = pygame.image.load("Setzling.png")
            Setzling = pygame.transform.scale(Setzling, (30, 35))
            surface.blit(Setzling, (self.x * GRID_SIZE, self.y * GRID_SIZE))
        elif self.Wachstumsstadium == "Kleine Pflanze":
            Kleine_Pflanze = pygame.image.load("Kleine_Pflanze.png")
            Kleine_Pflanze = pygame.transform.scale(Kleine_Pflanze, (35, 35))
            surface.blit(Kleine_Pflanze, (self.x * GRID_SIZE, self.y * GRID_SIZE))
        elif self.Wachstumsstadium == "Vollausgewachsene Pflanze":
            Vollausgewachsene_Pflanze = pygame.image.load("Vollausgewachsene_Pflanze.png")
            Vollausgewachsene_Pflanze = pygame.transform.scale(Vollausgewachsene_Pflanze, (40, 40))
            surface.blit(Vollausgewachsene_Pflanze, (self.x * GRID_SIZE, self.y * GRID_SIZE))
            

    def get_info(self):
        info = {
            "Position": (self.x, self.y),
            "Pflanzenname": self.Pflanzenname,
            "Energie": self.Energie,
            "Alter": self.Alter,
            "Wachstumsstadium": self.Wachstumsstadium,
            "Eltern": self.Eltern.Pflanzenname if self.Eltern else "Keine",
            "Wetterschäden": self.Wetterschäden,
            "Mutationen": self.Mutationen
        }
        return info

# Erstelle die ersten 10 Pflanzen
creatures = [Creature(random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1)) for _ in range(10)]

# Statistiken Updaten
def Wachstumsstadium(creature):
    if creature.Alter < 5:
        creature.Wachstumsstadium = "Setzling"
    elif creature.Alter < 10:
        creature.Wachstumsstadium = "Kleine Pflanze"
    else:
        creature.Wachstumsstadium = "Vollausgewachsene Pflanze"
        


# Funktionen für die UI der Pflanzen
def get_clicked_creature(mouse_pos):     # Überprüft ob eine Pflanze angeklickt wurde
    for creature in creatures:
        x_start = creature.x * GRID_SIZE
        y_start = creature.y * GRID_SIZE
        x_end = x_start + GRID_SIZE
        y_end = y_start + GRID_SIZE

        if x_start <= mouse_pos[0] <= x_end and y_start <= mouse_pos[1] <= y_end:
            return creature
    return None
    
# UI     
def draw_info_panel(surface, creature, x_offset=510):
    if creature:
        info = creature.get_info()
        font = pygame.font.SysFont("Arial", 16)
        y_offset = 10
        for key, value in info.items():
            text = font.render(f"{key}: {value}", True, DARKGREEN)
            surface.blit(text, (x_offset, y_offset)) 
            y_offset += 20

    
    

# Tag Nacht Zyklus
def Tag_Nacht_Zyklus():
    global Tag, Farbe, Aktueller_Tag, Tag_Seasons, Season
    Aktueller_Tag = 1
    Tag_Seasons = 1
    Season  = "Frühling"
    Tag = True
    while True:
        if Tag == True:
            Farbe = WHITE
            debugprint()
            Seasons()
            Aktueller_Tag += 1
            Tag_Seasons += 1
            time.sleep(5)
            Tag = False
        else:
            Farbe = GRAY
            debugprint()
            Seasons()
            Aktueller_Tag += 1
            Tag_Seasons += 1
            time.sleep(5)
            Tag = True

# Seasons
def Seasons():
    global Season, Tag_Seasons
    if Tag_Seasons == 30:
        Season = "Sommer"
    elif Tag_Seasons == 60:
        Season = "Herbst"
    elif Tag_Seasons == 90:
        Season = "Winter"
    elif Tag_Seasons == 120:
        Tag_Seasons = 0
        Season = "Frühling"

# UI aktualisieren
def update_ui():
    screen.fill(BLACK)
    for creature in creatures:
        creature.draw(screen)
    pygame.display.flip()
        
def add_plant_to_ui(creature):
    creature.draw(screen)
    pygame.display.flip()
    
# Lebensparameter
global Licht, Wasserverbrauch, Grundwasserstand
Sturmschädenenergie = 0
Sturmschädenwasser = 0
Tag = True
Licht = 100
def Lebensprozesse():
    global Licht, Tag, Wasserverbrauch, Grundwasserstand, Bodennährstoffgehalt
    while True:
        if Tag == True:
            for creature in creatures:
                Licht = 100
                # Energieverbrauch
                Energieverbrauch = creature.Energieverbrauch + Sturmschädenenergie
                creature.Energie -= Energieverbrauch 
                creature.Alter += 1
                Nährstoffverbrauch(creature)
                Wachstumsstadium(creature)
                # Wasserverbrauch
                if Grundwasserstand > 0:
                    Wasserverbrauch = creature.Wasserverbrauch + Sturmschädenwasser
                    Grundwasserstand -= Wasserverbrauch
                # Tod?
                if creature.Energie <= 0:
                    creatures.remove(creature)
                    Nährstoffwiederherstellung()
                    update_ui()
                    continue
                # Energieregeneration
                if Grundwasserstand and Bodennährstoffgehalt > 0:
                    creature.Energie += random.randint(1, 5)
            time.sleep(5)
        elif Tag == False:
            for creature in creatures:
                Licht = 0
                # Energieverbrauch
                Energieverbrauch = creature.Energieverbrauch + Sturmschädenenergie
                creature.Energie -= Energieverbrauch    # Mal gucken ob das so passt
                creature.Alter += 1
                Nährstoffverbrauch(creature)
                Wachstumsstadium(creature)
                # Wasserverbrauch
                if Grundwasserstand > 0:
                    Wasserverbrauch = creature.Wasserverbrauch + Sturmschädenwasser
                    Grundwasserstand -= Wasserverbrauch
                # Tot?
                if creature.Energie <= 0:
                    creatures.remove(creature)
                    Nährstoffwiederherstellung()
                    update_ui()
                    continue
                # Energieregeneration
                if Grundwasserstand and Bodennährstoffgehalt > 0:
                    creature.Energie += random.randint(1, 5)
            time.sleep(5)
            
        
# Nährstoffe       
global Bodennährstoffgehalt  
Bodennährstoffgehalt = 3000
def Nährstoffwiederherstellung():
    global Bodennährstoffgehalt
    Dazu = creature.Alter * 50             # Mal gucken ob das so passt
    Bodennährstoffgehalt += Dazu
def Nährstoffverbrauch(creature):
    global Bodennährstoffgehalt        
    Bodennährstoffgehalt -= creature.Nahrungsverbrauch 
            
# Wetter
aktuelles_Wetter = "Bewölkt"
Grundwasserstand = 1000  
def Wetter():
    global aktuelles_Wetter, Grundwasserstand
    
    # Chance auf Wetteränderung
    ChangeWetter = random.randint(1, 100)
    
    # Wetterbestimmung je nach Jahreszeit
    if Season == "Frühling":
        # Säureregen (1% Chance)
        if ChangeWetter <= 1:
            aktuelles_Wetter = "Säureregen"
        # Hitzewelle (1% Chance)
        elif ChangeWetter <= 2:
            aktuelles_Wetter = "Hitzewelle"
        # Hagel (1% Chance)
        elif ChangeWetter <= 3:
            aktuelles_Wetter = "Hagel"
        # Sturm (2% Chance)
        elif ChangeWetter <= 5: 
            aktuelles_Wetter = "Sturm"
        # Gewitter (5% Chance)
        elif ChangeWetter <= 10:  
            aktuelles_Wetter = "Gewitter"
        # Sonnig (10% Chance)
        elif ChangeWetter <= 20:  
            aktuelles_Wetter = "Sonne"
        # Kältefront (15% Chance)
        elif ChangeWetter <= 35: 
            aktuelles_Wetter = "Kältefront"
        # Regen (30% Chance)
        elif ChangeWetter <= 65:  
            Regenmenge = random.randint(500, 2000)
            Grundwasserstand += Regenmenge
            aktuelles_Wetter = "Regen"
            print(f"Regenmenge: {Regenmenge}")
        # Normales Wetter (35% Chance)
        else:
            aktuelles_Wetter = "Bewölkt"
        Pflanzenschäden()
            
    elif Season == "Sommer":
        # Säureregen (1% Chance)
        if ChangeWetter <= 1:
            aktuelles_Wetter = "Säureregen"
        # Hagel (2% Chance)
        elif ChangeWetter <= 3: 
            aktuelles_Wetter = "Hagel"
        # Sturm (8% Chance)
        elif ChangeWetter <= 11:  
            aktuelles_Wetter = "Sturm"
        # Sonnig (10% Chance)
        elif ChangeWetter <= 21:  
            aktuelles_Wetter = "Sonne"
        # Gewitter (15% Chance)
        elif ChangeWetter <= 36:  
            aktuelles_Wetter = "Gewitter"
        # Hitzewelle (15% Chance)
        elif ChangeWetter <= 51:  
            aktuelles_Wetter = "Hitzewelle"
        # Regen (40% Chance)
        elif ChangeWetter <= 91:  
            Regenmenge = random.randint(500, 2000)
            Grundwasserstand += Regenmenge
            aktuelles_Wetter = "Regen"
            print(f"Regenmenge: {Regenmenge}")
        # Normales Wetter (9% Chance)
        else:
            aktuelles_Wetter = "Bewölkt"
        Pflanzenschäden()
            
    elif Season == "Herbst":
        # Säureregen (1% Chance)
        if ChangeWetter <= 1:
            aktuelles_Wetter = "Säureregen"
        # Kältefront (1% Chance)
        elif ChangeWetter <= 2:  
            aktuelles_Wetter = "Kältefront"
        # Hagel (2% Chance)
        elif ChangeWetter <= 4:  
            aktuelles_Wetter = "Hagel"
        # Gewitter (8% Chance)
        elif ChangeWetter <= 12:  
            aktuelles_Wetter = "Gewitter"
        # Sonnig (8% Chance)
        elif ChangeWetter <= 20:  
            aktuelles_Wetter = "Sonne"
        # Sturm (12% Chance)
        elif ChangeWetter <= 32:  
            aktuelles_Wetter = "Sturm"
        # Regen (40% Chance)
        elif ChangeWetter <= 72:  
            Regenmenge = random.randint(500, 2000)
            Grundwasserstand += Regenmenge
            aktuelles_Wetter = "Regen"
            print(f"Regenmenge: {Regenmenge}")
        # Normales Wetter (28% Chance)
        else:
            aktuelles_Wetter = "Bewölkt"
        Pflanzenschäden()
            
    elif Season == "Winter":
        # Säureregen (1% Chance)
        if ChangeWetter <= 1:
            aktuelles_Wetter = "Säureregen"
        # Gewitter (2% Chance)
        elif ChangeWetter <= 3:  
            aktuelles_Wetter = "Gewitter"
        # Sonnig (8% Chance)
        elif ChangeWetter <= 11:  
            aktuelles_Wetter = "Sonne"
        # Sturm (12% Chance)
        elif ChangeWetter <= 23:  
            aktuelles_Wetter = "Sturm"
        # Regen (30% Chance)
        elif ChangeWetter <= 53:  
            Regenmenge = random.randint(500, 2000)
            Grundwasserstand += Regenmenge
            aktuelles_Wetter = "Regen"
            print(f"Regenmenge: {Regenmenge}")
        # Kältefront (45% Chance)
        elif ChangeWetter <= 98:  
            aktuelles_Wetter = "Kältefront"
        # Normales Wetter (2% Chance)
        else:
            aktuelles_Wetter = "Bewölkt"
        Pflanzenschäden()
            
def Pflanzenschäden():
    if aktuelles_Wetter == "Säureregen":
        for creature in creatures:
            Schadenroll = random.randint(1, 100)
            if Schadenroll >= 5:
                creature.Wetterschäden.append("Säureschaden")
    elif aktuelles_Wetter == "Hagel":
        for creature in creatures:
            Schadenroll = random.randint(1, 100)
            if Schadenroll <= 5:
                creature.Wetterschäden.append("Hagelschaden")
    elif aktuelles_Wetter == "Sturm":
        for creature in creatures:
            Schadenroll = random.randint(1, 100)
            if Schadenroll >= 15:
                creature.Wetterschäden.append("Ast abgebrochen")
    else:
        Dicerollinfektion = random.randint(1, 100000)
        for creature in creatures:
            if Dicerollinfektion <= 1000:
                creature.Wetterschäden.append("Infektion")
            
def Pflanzenschädeneffekt():
    global Sturmschädenenergie, Sturmschädenwasser
    for creature in creatures:
        if "Säureschaden" in creature.Wetterschäden:
            creature.Energie -= 10
            Sturmschädenenergie = 3
        if "Hagelschaden" in creature.Wetterschäden:
            creature.Energie -= 20
            Sturmschädenenergie = 2
        if "Ast abgebrochen" in creature.Wetterschäden:
            creature.Energie -= 15
            Sturmschädenenergie = 1
            Sturmschädenwasser = 2
        if "Infektion" in creature.Wetterschäden:
            creature.Energie -= 25
            Sturmschädenenergie = 5
            Sturmschädenwasser = 5
            
# Vortpflanzen
def Vortpflanzung(creature):
    if creature.Energie > 80 and creature.Alter > 5:
        for _ in range(5):  # Bis zu 5 Versuche, einen freien Platz zu finden
            x1 = creature.x + random.choice([-2, -1, 0, 1, 2])
            y1 = creature.y + random.choice([-2, -1, 0, 1, 2])

        # Stelle sicher, dass die neuen Positionen innerhalb des Grids liegen
        x1 = max(0, min(x1, GRID_WIDTH - 1))
        y1 = max(0, min(y1, GRID_HEIGHT - 1))

        # Überprüfen, ob bereits eine Pflanze auf der Position existiert
        if any(c.x == x1 and c.y == y1 for c in creatures):
            return  # Falls besetzt keine neue Pflanze erzeugen

        # Erstelle eine neue Pflanze mit den Elterninformationen
        new_creature = Creature(x1, y1, eltern=creature)
        creatures.append(new_creature)
        creature.Energie -= 40
        add_plant_to_ui(new_creature)


#Debug

def debugprint():
    print("Tag: " +  str(Aktueller_Tag))
    print(f"Anzahl Pflanzen: {len(creatures)}")
    print(f"Gesamtenergie: {sum(creature.Energie for creature in creatures)}")
    print(f"Bodennährstoffe: {Bodennährstoffgehalt}")
    print(f"Grundwasserstand: {Grundwasserstand}")
    print(f"Wetter: {aktuelles_Wetter}")
    print("-----------------------------")



# Ganzes Loop Zeug und Threads
def Vortpflanzungszyklus():
    while True:
        for creature in creatures[:]:
            Vortpflanzung(creature)
        time.sleep(5)
        
def Wetterzyklus():
    while True:
        Wetter()
        Datenspeicherung()
        time.sleep(5)
        
        
def Leere_Dateien():
    open("Data\\Anzahlpflanzen.txt", "w").close()
    open("Data\\Bodennährstoffe.txt", "w").close()
    open("Data\\Grundwasserstand.txt", "w").close()
    open("Data\\Wetter.txt", "w").close()

def Datenspeicherung():
    with open("Data\Anzahlpflanzen.txt", "a") as f:
        f.write(f"Tag: {Aktueller_Tag}\n")
        f.write(f"Anzahl Pflanzen: {len(creatures)}\n")
    with open("Data\Bodennährstoffe.txt", "a") as f:
        f.write(f"Tag: {Aktueller_Tag}\n")
        f.write(f"Bodennährstoffe: {Bodennährstoffgehalt}\n")
    with open("Data\Grundwasserstand.txt", "a") as f:
        f.write(f"Tag: {Aktueller_Tag}\n")
        f.write(f"Grundwasserstand: {Grundwasserstand}\n")
    with open("Data\Wetter.txt", "a") as f:
        f.write(f"Tag: {Aktueller_Tag}\n")
        f.write(f"Wetter: {aktuelles_Wetter}\n")
    with open("Data\Gesamtenergie.txt", "a") as f:
        f.write(f"Tag: {Aktueller_Tag}\n")
        f.write(f"Gesamtenergie: {sum(creature.Energie for creature in creatures)}\n")
    
    
    
Farbe = WHITE
threading.Thread(target=Tag_Nacht_Zyklus, daemon=True).start()
threading.Thread(target=Lebensprozesse, daemon=True).start()
threading.Thread(target=Vortpflanzungszyklus, daemon=True).start()
threading.Thread(target=Wetterzyklus, daemon=True).start()

def draw_grid():
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, BLACK, (0, y), (WIDTH, y))

running = True
selected_creature = None  # Speichert die ausgewählte Pflanze
show_info_window = False

Leere_Dateien()

while running:
    screen.fill(Farbe)
    draw_grid()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_pos = pygame.mouse.get_pos()
            selected_creature = get_clicked_creature(mouse_pos)
            if selected_creature:
                show_info_window = True  # Info-Fenster anzeigen

    # Zeichne alle Pflanzen
    for creature in creatures:
        creature.draw(screen)
    
    # Zeichne das Info-Fenster, wenn eine Pflanze ausgewählt wurde
    if show_info_window and selected_creature:
        # Zeichne ein Rechteck als Hintergrund für das Info-Fenster
        pygame.draw.rect(screen, WHITE, (WIDTH - INFO_WIDTH, 0, INFO_WIDTH, INFO_HEIGHT))
        pygame.draw.rect(screen, BLACK, (WIDTH - INFO_WIDTH, 0, INFO_WIDTH, INFO_HEIGHT), 2)  # Rahmen
        # Zeichne die Informationen der Pflanze
        draw_info_panel(screen, selected_creature)

    pygame.display.flip()
    clock.tick(60)