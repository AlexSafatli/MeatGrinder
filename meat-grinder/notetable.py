# notetable.py
# -------------------------
# Summer 2013; Christian Blouin
# -------------------------
# Library for handling notes for
# meatgrinder.

# Table

notes = {'Skull':[1,3],'Face':[1,4],'Right Leg':[5],\
       'Right Arm':[5,6],'Torso':[18],\
       'Abdomen':[20],'Left Arm':[5,6],\
       'Left Leg':[5],'Hand':[6,8,9],\
       'Foot':[8,9],'Neck':[1,10],'Vitals':[1,11],\
       'Eye':[1,2],'Ear':[1,12],'Nose':[1,15],\
       'Jaw':[1,13],'Spine':[1,16], 'Leg Vascular':[17],'Arm Vascular':[6,17],\
       'Neck Vascular':[17],'Elbow':[14],'Knee':[14],'Shoulder':[14],'Wrist':[14],'Ankle':[14],\
       'Groin':[1,7],'Pelvis':[19],'Digestive Tract':[21], \
       'Heart':[1,11], 'Cheek':[1,4],\
       'Forearm':[5,6],'Elbow':[5,6,14],'Upper Arm':[5,6],'Shoulder':[5,6,14],\
       'Shin':[5],'Knee':[5,14],'Thigh':[5] }

# Class

class process_notes:
    
    def __init__(self,locator):
        self.loc = locator
        self.notes = []
        
        # Process notes.
        for i in notes[locator.location[-1]]:
            # Call methods from a generated method's name
            if hasattr(self, 'Note%d'%(i)):
                getattr(self,'Note%d'%(i))()
                
        # Veins as targets and sublocation
        if 'Vascular' in locator.location[0]:
            self.Note17()
        
        # Avoid duplication
        locator.notes = []
        for i in self.notes:
            if i not in locator.notes:
                locator.notes.append(i)
                
    def Note1(self):
        if not 'Abdomen' in self.loc.location[0]:
            self.notes.append("Attacks that miss by 1 hit the Torso instead.")
        
    def Note2(self):
        self.notes.append('Eyes are treated as Skull but without DR2.')
        self.notes.append('Any armor covering the face will stop an eye hit unless the blow specifically targets this sub-location.')
        self.Note3()
        
    def Note3(self):
        loc = self.loc
        self.notes.append('Skulls gets a DR2.')
        if type(loc.multiplier) == type(0.0):
            loc.multiplier = 4.0
        if not loc.atktype == 'tox':
            self.notes.append('Knockdown rolls are at -10.')
            self.notes.append('Use Critical Head Blow table (B556).')
        
    def Note4(self):
        loc = self.loc
        self.notes.append('Ignore helmet DR if open-face.')
        self.notes.append('Knockdown rolls are at -5.')
        self.notes.append('Use Critical Head Blow table (B556).')
        if loc.atktype == 'cor':
            loc.multiplier = 1.5
            self.notes.append('Major wound blinds one eye. Both for >HP.')
        self.notes.append('Random attack from behind hit skull.')
        
    def Note5(self):
        loc = self.loc
        if loc.atktype in ['pi+', 'pi++', 'imp']:
            loc.multiplier = 1.0
        self.notes.append('Damage over HP/2 is lost.')
        
    def Note6(self):
        self.notes.append('If holding a shield, -4 to hit for arm, -8 to hit for hand.')
        
    def Note7(self):
        loc = self.loc
        if loc.atktype == 'cr':
            self.notes.append('Males suffer double shock.')
            self.notes.append('Knockdown roll at -5.')
        else:
            self.notes.append('Treat as torso wound.')
            
    def Note8(self):
        loc = self.loc
        if loc.atktype in ['pi+', 'pi++', 'imp']:
            loc.multiplier = 1.0 
        self.notes.append('Damage over HP/4 is lost.')
        
    def Note9(self):
        loc = self.loc
        lcs = list(loc.location)
        if loc.roll() <= 10:
            lcs[0] = 'Right ' + lcs[0]
        else:
            lcs[0] = 'Left ' + lcs[0]
        loc.location = tuple(lcs)
            
    def Note10(self):
        loc = self.loc
        if loc.atktype in ['cr', 'cor']:
            loc.multiplier = 1.5
        elif loc.atktype == 'cut':
            loc.multiplier = 2.0
            
    def Note11(self):
        loc = self.loc
        if 'pi' in loc.atktype or loc.atktype == 'imp':
            loc.multiplier = 3.0
        elif loc.atktype == 'tbb':
            loc.multiplier = 2.0
        elif loc.atktype == 'cr':
            loc.multiplier = 1.0
        self.notes.append('Knockdown roll at -5.')
        
    def Note12(self):
        loc = self.loc
        if loc.atktype == 'cut':
            self.notes.append('Max damage HP/4 for cut.')
            self.notes.append('Severed on major wounds.')
            
    def Notes13(self):
        loc = self.loc
        if loc.atktype == 'cr':
            self.notes.append('Knockdown at -1 for cr.')
            
    def Note14(self):
        self.notes.append('HT-1 to recover from crippling.')
        self.notes.append('Miss by 1: hit the extremity or limb instead.')
        
    def Note15(self):
        # Treat as face hit
        loc = self.loc
        self.Note1()
        self.Note3()
        if loc.atktype == 'cut':
            self.notes.append('HP/2 severs the Nose. No knockdown penalty. Appearance -2.')
        self.notes.append('HP/4 cause no sense of Taste/Smell until healed.')
        
    def Note16(self):
        self.notes.append('DR3')
        self.notes.append('If shock penalty: roll vs. knockdown.')
        self.notes.append('Automatic stun/knockdown for Major Wound.')
        
    def Note17(self):
        if 'Damage over HP/2 is lost.' in self.notes:
            self.notes.remove('Damage over HP/2 is lost.')
        loc = self.loc
        self.notes.append('No maximum damage to body part.')
        self.notes.append('Cause Severe bleeding (every 30s).')
        if type(loc.multiplier) == type(0.0):
            loc.multiplier += 0.5
        
    def Note18(self):
        loc = self.loc
        if loc.atktype == 'cut':
            self.notes.append('Spine hit if from behind.')
            
    def Note19(self):
        self.notes.append('Fall down on major wound.')
        self.notes.append('Acquire Lame (missing leg) until healed.')
        self.notes.append('Cannot fight standing up.')
        
    def Note20(self):
        # Handled earlier.
        pass
    
    def Note21(self):
        self.notes.append('HT-3 on check vs. infections.')
        
        
            
            
        
        
        
                        
        
