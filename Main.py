import pygame
import random
import threading 
import time
import random

###################Plant_Simulation V_0.2#########################################
###########Todo Liste#######################################
# 3. Wetter soll Pflanzen beschädigen 
# 7. Mutationen vllt einbauen
# 8. Verschiedene Wetter einbauen -> Gewitter, Tornado, Feuersturm, Flut, Hagel, ...
# 9. Seasonen einbauen -> Winter, Sommer, Herbst, Frühling
# 10. Geschwindigkeit einfach anpassbar -> Config Datei
# 11. UI verbessern -> Graphen, Komplizierter: Pflanze anklicken und dann öffnet sich ein seperates Fenster mit infos über die Pflanze 
# -> Mutierte eigenschaften anzeigen
# 12. Regenanimation (Einzelne random Pixel die sich Bläuchlich färben)
###################################################################
######################Schönheit#####################################
# 2.  
######################Ganz Späte Ideen##############################
# 1. Stammbaum
# 2. Logisch generierte Pflanzennamen                                                                                     ###### So halb fertig
# 3. Config kann viele Faktoren ändern (Z.B Regenwahrscheinlichkeit, Welche Wetter es geben kann, ...)
# 4. Größeren Bildschirm für Raspi kaufen und darauf das laufen lassen auch als schöne und interesannte Deko              ###### Echt gute Idee

############################################################
#####################Bug Liste################################
#Wetter Funktioniert noch nicht ganz



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
        self.Wasserverbrauch = 0
        self.Energieverbrauch = 0
        #Wetterschäden
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
global Energieverbrauch, WasserundNahrungsVerbrauch, Licht, Wasserverbrauch, Grundwasserstand
Tag = True
WasserundNahrungsVerbrauch = 5
Energieverbrauch = 4
Licht = 100
def Lebensprozesse():
    global Licht, Tag, Wasserverbrauch, Grundwasserstand, Bodennährstoffgehalt
    while True:
        if Tag == True:
            for creature in creatures:
                Wasserverbrauch = random.randint(1, WasserundNahrungsVerbrauch)
                Licht = 100
                # Energieverbrauch
                creature.Energie -= random.randint(1, Energieverbrauch) + (creature.Alter // 15)   # Mal gucken ob das so passt
                creature.Alter += 1
                Nährstoffverbrauch()
                Wachstumsstadium(creature)
                # Wasserverbrauch
                wasserverbrauch = Wasserverbrauch + (creature.Alter // 20)
                if Grundwasserstand > 0:
                    Grundwasserstand -= wasserverbrauch
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
                Wasserverbrauch = random.randint(1, WasserundNahrungsVerbrauch)
                Licht = 0
                # Energieverbrauch
                creature.Energie -= random.randint(1, Energieverbrauch) + (creature.Alter // 15)    # Mal gucken ob das so passt
                creature.Alter += 1
                Nährstoffverbrauch()
                Wachstumsstadium(creature)
                # Wasserverbrauch
                wasserverbrauch = Wasserverbrauch + (creature.Alter // 20)
                if Grundwasserstand > 0:
                    Grundwasserstand -= wasserverbrauch
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
def Nährstoffverbrauch():
    global Bodennährstoffgehalt
    Weg = random.randint(1, 2)                # Mal gucken ob das so passt            
    Bodennährstoffgehalt -= Weg  
            
# Wetter
aktuelles_Wetter = "Bewölkt"
Grundwasserstand = 1000  
def Wetter():
    global aktuelles_Wetter, Grundwasserstand
##################Season Frühling#########################
    if Season == "Frühling":
        # Chance auf Wetteränderung
        ChangeWetter = random.randint(1, 100)
        print(ChangeWetter)
        
        # Säureregen (1% Chance)
        if ChangeWetter <= 1:
            aktuelles_Wetter = "Säureregen"
            time.sleep(5)
        # Hitzewelle (1% Chance)
        elif ChangeWetter <= 2:
            aktuelles_Wetter = "Hitzewelle"
            time.sleep(5)            
        # Hagel (1% Chance)
        elif ChangeWetter <= 3:
            aktuelles_Wetter = "Hagel"
            time.sleep(5)
        # Sturm (2% Chance)
        elif ChangeWetter <= 2:
            aktuelles_Wetter = "Sturm"
            time.sleep(5)            
        # Gewitter (5% Chance)
        elif ChangeWetter <= 5:
            aktuelles_Wetter = "Gewitter"
            time.sleep(5)
        # Sonnig (10% Chance)
        elif ChangeWetter <= 10:
            aktuelles_Wetter = "Sonne"
            time.sleep(5)
        # Kältefront (15% Chance)
        elif ChangeWetter <= 15:
            aktuelles_Wetter = "Kältefront"
            time.sleep(5)
        # Regen (30% Chance)
        elif ChangeWetter <= 30:
            Regenmenge = random.randint(500, 2000)
            Grundwasserstand += Regenmenge
            aktuelles_Wetter = "Regen"
            time.sleep(5)            
        # Normales Wetter (35% Chance)
        else:
            aktuelles_Wetter = "Bewölkt"
            time.sleep(5)
##################Season Sommer#########################
    if Season == "Sommer":
        # Chance auf Wetteränderung
        ChangeWetter = random.randint(1, 100)
        
        # Säureregen (1% Chance)
        if ChangeWetter <= 1:
            aktuelles_Wetter = "Säureregen"
            time.sleep(5)
        # Kältefront (0% Chance)
        elif ChangeWetter <= 0:
            aktuelles_Wetter = "Kältefront"
            time.sleep(5)            
        # Hagel (2% Chance)
        elif ChangeWetter <= 2:
            aktuelles_Wetter = "Hagel"
            time.sleep(5)
        # Sturm (8% Chance)
        elif ChangeWetter <= 8:
            aktuelles_Wetter = "Sturm"
            time.sleep(5)     
        # Sonnig (10% Chance)
        elif ChangeWetter <= 10:
            aktuelles_Wetter = "Sonne"
            time.sleep(5)                   
        # Gewitter (15% Chance)
        elif ChangeWetter <= 15:
            aktuelles_Wetter = "Gewitter"
            time.sleep(5)
        # Hitzewelle (15% Chance)
        elif ChangeWetter <= 15:
            aktuelles_Wetter = "Hitzewelle"
            time.sleep(5)
        # Regen (40% Chance)
        elif ChangeWetter <= 40:
            Regenmenge = random.randint(500, 2000)
            Grundwasserstand += Regenmenge
            aktuelles_Wetter = "Regen"
            time.sleep(5)            
        # Normales Wetter (9% Chance)
        else:
            aktuelles_Wetter = "Bewölkt"
            time.sleep(5)
##################Season Herbst#########################
    if Season == "Herbst":
        # Chance auf Wetteränderung
        ChangeWetter = random.randint(1, 100)
        
        # Säureregen (1% Chance)
        if ChangeWetter <= 1:
            aktuelles_Wetter = "Säureregen"
            time.sleep(5)
        # Hitzewelle (0% Chance)
        elif ChangeWetter <= 0:
            aktuelles_Wetter = "Hitzewelle"
            time.sleep(5)
        # Kältefront (1% Chance)
        elif ChangeWetter <= 1:
            aktuelles_Wetter = "Kältefront"
            time.sleep(5)                        
        # Hagel (2% Chance)
        elif ChangeWetter <= 2:
            aktuelles_Wetter = "Hagel"
            time.sleep(5)
        # Gewitter (8% Chance)
        elif ChangeWetter <= 8:
            aktuelles_Wetter = "Gewitter"
            time.sleep(5)
        # Sonnig (8% Chance)
        elif ChangeWetter <= 8:
            aktuelles_Wetter = "Sonne"
            time.sleep(5)
        # Sturm (12% Chance)
        elif ChangeWetter <= 12:
            aktuelles_Wetter = "Sturm"
            time.sleep(5)
        # Regen (40% Chance)
        elif ChangeWetter <= 40:
            Regenmenge = random.randint(500, 2000)
            Grundwasserstand += Regenmenge
            aktuelles_Wetter = "Regen"
            time.sleep(5)            
        # Normales Wetter (28% Chance)
        else:
            aktuelles_Wetter = "Bewölkt"
            time.sleep(5)
##################Season Winter#########################
    if Season == "Winter":
        # Chance auf Wetteränderung
        ChangeWetter = random.randint(1, 100)
        
        # Säureregen (1% Chance)
        if ChangeWetter <= 1:
            aktuelles_Wetter = "Säureregen"
            time.sleep(5)
        # Hitzewelle (0% Chance)
        elif ChangeWetter <= 0:
            aktuelles_Wetter = "Hitzewelle"
            time.sleep(5)            
        # Hagel (0% Chance)
        elif ChangeWetter <= 0:
            aktuelles_Wetter = "Hagel"
            time.sleep(5)
        # Gewitter (2% Chance)
        elif ChangeWetter <= 2:
            aktuelles_Wetter = "Gewitter"
            time.sleep(5)
        # Sonnig (8% Chance)
        elif ChangeWetter <= 8:
            aktuelles_Wetter = "Sonne"
            time.sleep(5)
        # Sturm (12% Chance)
        elif ChangeWetter <= 12:
            aktuelles_Wetter = "Sturm"
            time.sleep(5)
        # Regen (30% Chance)
        elif ChangeWetter <= 30:
            Regenmenge = random.randint(500, 2000)
            Grundwasserstand += Regenmenge
            aktuelles_Wetter = "Regen"
            time.sleep(5)            
        # Kältefront (45% Chance)
        elif ChangeWetter <= 45:
            aktuelles_Wetter = "Kältefront"
            time.sleep(5)
        # Normales Wetter (2% Chance)
        else:
            aktuelles_Wetter = "Bewölkt"
            time.sleep(5)
    aktuelles_Wetter = "Bewölkt"
            
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
        time.sleep(5)
        
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