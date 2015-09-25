# meatgrinder.py
# -------------------------
# Summer 2013; Alex Safatli/Christian Blouin
# -------------------------
# API for handling hit location
# determination using GURPS rules.

import random as r
import notetable, woundtable
from stattracker import GrindHit, Counter
from google.appengine.ext import db

# Language Literals for the HTML interface.

types = [['cut','Cutting'],['imp','Impaling'],
         ['cr','Crushing'],['pi-','Piercing, Small'],
         ['pi','Piercing, Normal'],['pi+','Piercing, Large'],
         ['pi++','Piercing, Huge'],['aff','Affliction'],
         ['burn','Burning'],['cor','Corrosion'],
         ['fat','Fatigue'],['tox','Toxic']]

parts = notetable.notes.keys()
parts.sort()

hitmod = {'Skull':'-7/-5','Face':'-5/-7',
          'Right Leg':-2,'Right Arm':-2,'Torso':0,
          'Abdomen':-1,'Left Arm':-2,'Forearm':-3,
          'Upper Arm':-3, 'Thigh':-3, 'Shin':-3,
          'Left Leg':-2,'Hand':-4,'Foot':-4,
          'Neck':-5,'Vitals':-3,'Eye':-9,'Ear':-7,
          'Nose':-7,'Jaw':-6,'Spine':-8,
          'Arm Vascular':-5,'Leg Vascular':-5,
          'Neck Vascular':-8,'Elbow':-5,'Knee':-5,
          'Shoulder':-5,'Wrist':-7,'Ankle':-7,
          'Groin':-3,'Pelvis':-3,'Digestive Tract':-2,
          'Heart':-5,'Cheek':-6}

# Rule Literals

# Using Hit Location & Damage Modifier Table; B552
# http://forums.sjgames.com/showthread.php?t=76205

hit = {3:'Skull',4:'Skull',5:'Face',6:'Right Leg',
       7:'Right Leg',8:'Right Arm',9:'Torso',
       10:'Torso',11:'Abdomen',12:'Left Arm',
       13:'Left Leg',14:'Left Leg',15:'Hand',
       16:'Foot',17:'Neck',18:'Neck'}

# Using Damage Type and Multipliers Table

mult = {'aff':None,'burn':1.0,'cor':1.0,'cr':1.0,
       'cut':1.5,'fat':None,'imp':2.0,'pi-':0.5,
       'pi':1.0,'pi+':1.5,'pi++':2.0,'spec':None,
       'tbb':1.0,'tox':1.0}

# Realistic Injury (Martial Arts, p. 136)
# Possible thresholds are -1 (all injury), HP/10, HP/5

franyaction = 'for any action involving that location'
arminj = [['slight','-1 DX %s (incl. two-handed tasks).' \
          % (franyaction)],['HP/5-HP/3','-3 DX %s (incl. two-handed tasks).' \
          % (franyaction)],['HP/3-HP/2','The arm is almost broken; Will roll to use; success at -5 DX.'],\
          ['>HP/2','Crippled'],['>HP','Severed']]
leginj = [['slight','-1 DX %s and with good leg if standing.' \
          % (franyaction)],['HP/5-HP/3','-3 DX %s and -1 with good leg if standing.' \
          % (franyaction)],['HP/3-HP/2','The leg is almost broken; Will roll to use.'],\
          ['>HP/2','Crippled'],['>HP','Severed']]
quarinj = [['>HP/4','Crippled'],['>HP/2','Severed']]

inj = {'Right Arm':arminj,'Left Arm':arminj,'Arm': arminj,\
       'Right Leg':leginj,'Left Leg':leginj,'Leg': arminj,\
       'Torso':[['HP/3','-1 DX for all purposes.'],['HP/2','-2 DX, Move is 80 percent normal.'],
                ['>2/3 HP','-3 DX, Move is 50 percent normal.']],\
       'Eye':[['HP/10','Blinded'],['HP/10','Destroyed']],\
       'Right Hand': quarinj,'Left Hand': quarinj,'Hand': quarinj,\
       'Right Foot': quarinj,'Left Foot': quarinj,'Foot': quarinj,\
       'Nose': quarinj,\
       'Spine': [['HP/1','Crippled']]}

# Random Number Generation

class dice:
    def __init__(self,num,sides):
        self.num = num
        self.sides = sides
    def roll(self):
        result = 0
        for i in xrange(self.num):
            result += r.randint(1,self.sides)
        return result

# Location Class

class locator:
    
    def __init__(self,realistic,facesub):
        
        # Location (string).
        self.location = None
        
        # Damage Type (string).
        self.atktype = None
        
        # Damage multiplier (float).
        self.multiplier = 1.0
        
        # General message to pass to user (list of strings).
        self.notes = []
        
        # List of thresholds appropriate for location (dictionary of strings).
        self.threshold = None
        
        # If a wound were to occur, what would happen (string).
        self.wound = None
        
        # Dice roller instances.
        self.__dice__ = dice(3,6) # 3d6
        self.__1d__ = dice(1,6) # 1d6
        
        # Determine realistic, facesub filters.
        self.realistic = ('1' in realistic)
        self.facesub = ('1' in facesub)
        
    def get(self,atktype,location):
           
        # ---- Get location. ---------------------------- #
        
        # Read damage type.
        self.atktype = atktype
        
        # Determine location.
        if location == 'random':
            self.location = (hit[self.__dice__.roll()],)
        else: self.location = (location,)
        
        # Set multiplier.
        if atktype in mult: self.multiplier = mult[atktype]
        
        # ---- Handle thresholds and sublocations.  ---- #
        
        # Get location from fields.
        loc = self.location[0]
        # Auxiliary hit location dice.
        rl = self.__1d__.roll()         
        
        # Low Tech Hit for random location.
        if 'Arm' in loc or 'Leg' in loc:
            r2 = self.__1d__.roll()
            # Arm
            if 'Arm' in loc:
                if r2 <= 3: self.location = (loc, 'Forearm')
                elif r2 == 4: self.location = (loc, 'Elbow')
                elif r2 == 5: self.location = (loc, 'Upper Arm') 
                elif r2 == 6: self.location = (loc, 'Shoulder')   
            # Leg
            if 'Leg' in loc:
                if r2 <= 3: self.location = (loc, 'Shin')
                elif r2 == 4: self.location = (loc, 'Knee')
                elif r2 > 4: self.location = (loc, 'Thigh')  
                
        # Low Tech Hit for targetted location.
        if loc in ['Shin', 'Knee', 'Thigh']:
            self.location = ('Leg', loc)
            loc = 'Leg'
        elif loc in ['Forearm', 'Elbow', 'Upper Arm', 'Shoulder']:
            self.location = ('Arm', loc)    
            loc = 'Arm' 
        
        if (rl == 1): # vascular damage or not?
            
            # Arm or leg.
            if not 'Vascular' in loc and ('Arm' in loc or 'Leg' in loc) and not ('cr' in atktype):
                # vascular hit!
                # Get Side
                side = loc.split()[0]
                
                # Chunk
                if 'Arm' in loc: chunk = 'Arm'
                else: chunk = 'Leg'
                
                # Reformat locs
                if len(loc.split()) == 1:
                    self.location = (self.location[-1] ,'%s Vascular'%(chunk))
                else:
                    self.location = (side + ' ' + self.location[-1] ,'%s Vascular'%(chunk))   
                    
            # In the face.
            elif 'Face' in loc :
                if atktype in ['imp','burn'] or 'pi' in atktype:
                    self.location = (loc,'Skull')
                else: self.location = (loc,'Nose')  
                    
            # Hand or feet.
            elif 'Hand' in loc:
                if atktype in ['cr','cut','burn'] or 'pi' in atktype:
                    self.location = (r.choice(['Left','Right'])+ ' ' + loc,'Wrist')
            elif 'Foot' in loc:
                if atktype in ['cr','cut','burn'] or 'pi' in atktype:
                    self.location = (r.choice(['Left','Right'])+ ' ' + loc,'Ankle') 
                    
            # Neck or torso.
            elif 'Neck' in loc or 'Torso' in loc:
                if atktype in ['cut','imp','burn'] or 'pi' in atktype:
                    if 'Neck' in loc: self.location = (loc,'Neck Vascular')
                    else: self.location = (loc,'Vitals')
                        
        # Abdomen
        if 'Abdomen' == loc:
            if rl == 1: self.location = (loc, 'Vitals')
            elif rl <= 4: self.location = (loc, 'Digestive Tract')
            elif rl == 5: self.location = (loc, 'Pelvis')
            else: self.location = (loc, 'Groin')
                
        # Face sub-location (when not already resolved).
        if self.facesub and 'Face' == loc and len(self.location) == 1:
            # die
            r1 = self.__1d__.roll()
            # Subloc
            if r1 == 1: self.location = (loc, 'Jaw')
            elif r1 == 2: self.location = (loc, 'Nose')
            elif r1 == 3: self.location = (loc, 'Ear')
            elif r1 == 4 or r1 == 5: self.location = (loc, 'Cheek')           
            else: self.location = (loc, 'Eye')        
         
        # Set threshold dictionary; order.
        self.SetThreshold()

        # ---- Process notes, wounds. -------------------- #
        
        notetable.process_notes(self)
        woundtable.process_wounds(self)
        
        # ---- Process critical hits. -------------------- #
        
        if loc in ['Face', 'Skull', 'Eye', 
                   'Ear', 'Nose', 'Cheek', 
                   'Jaw']:
            self.CriticalHead()
        else: self.CriticalHit()        
        
        # ---- Save data to datastore. ----------------- #
        
        self.SaveStats(atktype,location)
        
    def roll(self):
        return self.__dice__.roll()
    
    def SetThreshold(self):
        # Build Thresholds from option and return the results
        franyaction = 'for any action involving that location'
        
        # Arms
        if self.realistic:
            arminj = [['1 HP and more','-1 DX %s (incl. two-handed tasks).' \
                  % (franyaction)],['over HP/5, up to HP/3','-3 DX %s (incl. two-handed tasks).' \
                  % (franyaction)],['over HP/3, up to HP/2','The arm is almost broken; Will roll to use; success at -5 DX.']]
        else:
            arminj = []
        #arminj.extend([['more than HP/2','Crippled'],['twice crippled','Severed']])
        
        # Legs
        if self.realistic:
            leginj = [['more than 1 HP','-1 DX %s and with good leg if standing.' \
                  % (franyaction)],['over HP/5, up to HP/3','-3 DX %s and -1 with good leg if standing.' \
                  % (franyaction)],['over HP/3, up to HP/2','The leg is almost broken; Will roll to use.']]
        else:
            leginj = []      
        #leginj.extend([['over HP/2','Crippled'],['twice crippled','Severed']])       
            
        # Torso
        if self.realistic:
            torsod = [['1 HP and more','-1 DX for all purposes.' \
                  ],['over HP/2','-2 DX Movement is 80% of normal.' \
                  ],['over 2/3HP','-3 DX. Movement is 50% of normal.']]
        else:
            torsod = None     
        
        # Extremites
        quarinj = [['over HP/3','Crippled'],['twice crippled','Severed']]
        
        # Joints
        jextre =  [['over HP/4','Crippled'],['twice crippled','Severed']]
        
        # Build full dictionary
        inj = {'Right Arm':arminj,'Left Arm':arminj,'Arm': arminj,\
               'Right Leg':leginj,'Left Leg':leginj,'Leg': arminj,\
               'Torso': torsod,\
               'Eye':[['over HP/10','Blinded'],['twice blinded','Destroyed']],\
               'Right Hand': quarinj,'Left Hand': quarinj,'Hand': quarinj,\
               'Right Foot': quarinj,'Left Foot': quarinj,'Foot': quarinj,\
               'Nose': jextre,\
               'Spine': [['over HP','Crippled']] } 
        
        for side in ['Left', 'Right']:
            for part in ['Forearm', 'Upper Arm']:
                inj [side + ' ' + part] = arminj + [['over HP/2','Crippled'],['twice crippled','Severed']] 
                inj [ part] = arminj + [['over HP/2','Crippled'],['twice crippled','Severed']]                 
            for part in ['Elbow', 'Shoulder']:
                inj [side + ' ' + part] = arminj[:-1] + [['over HP/3','Crippled'],['twice crippled','Severed']]
                inj [part] = arminj[:-1] + [['over HP/3','Crippled'],['twice crippled','Severed']]
            for part in ['Shin','Thigh']:
                inj [side + ' ' + part] = leginj + [['over HP/2','Crippled'],['twice crippled','Severed']] 
                inj [part] = leginj + [['over HP/2','Crippled'],['twice crippled','Severed']] 
            for part in ['Knee']:
                inj [side + ' ' + part] = leginj[:-1] + [['over HP/3','Crippled'],['twice crippled','Severed']]
                inj [part] = leginj[:-1] + [['over HP/3','Crippled'],['twice crippled','Severed']] 
            for part in ['Ankle', 'Wrist']:
                inj [side + ' ' + part] = [['over HP/4','Crippled'],['twice crippled','Severed']]
                inj [part] = [['over HP/4','Crippled'],['twice crippled','Severed']]            
        
        loc = self.location[-1]
        if loc in inj:
            self.threshold = inj[loc]
        if self.threshold == None:
            self.threshold = [['over HP/2','Major Wound']]        
        
    def SaveStats(self,atktype,location):
        # Update the overall counter (cheaper than to do a full DB query since there is no aggregate 
        # functions in the datastore query language
        cnt = db.get( db.Key.from_path('Counter', 'overall') )
        if not cnt:
            cnt = Counter(key_name='overall')
            cnt.count = 1
        else: cnt.count += 1
        cnt.put()        
        
        # So it can be written to the UI
        self.counter = cnt.count
        
        # Try to retrieve the entry
        q = GrindHit.all()
        q.filter('realistic =', bool(int(self.realistic)))
        q.filter('damage_type =', atktype)
        q.filter('is_random =', bool(location == 'random'))
        q.filter('location =', self.location[-1])
        
        gh = q.get()
        if gh:
            gh.count += 1
            gh.put()
            return
        
        # Case where the entity doesn't exist.
        gh = GrindHit(realistic=bool(int(self.realistic)),
                      damage_type=atktype,location=self.location[-1],
                      is_random=bool(location == 'random'),count = 1)
        gh.put()
        
    # Critical Hit
    def CriticalHit(self):
        r = self.__dice__.roll()
        if r in [3,18]: self.critical = '<em>Triple</em> damage.'
        elif r in [4,17]: self.critical = 'DR <em>halved</em>.'
        elif r in [5,16]: self.critical = '<em>Double</em> damage.'        
        elif r in [6,15]: self.critical = '<em>Maximum</em> damage.'    
        elif r in [7,13,14]: self.critical = 'Major injury <em>if</em> penetrating damage.'
        elif r in [8]: self.critical = '<em>Funny bone</em>: double shock, extremities crippled for 16-HT turns.'
        elif r in [12]: self.critical = 'Victim <em>drops</em> something.'
        else: self.critical = 'No active defense allowed.'
            
    # Critical head injuries
    def CriticalHead(self):
        r = self.__dice__.roll()
        if r == 3: self.critical = '<em>Maximum</em> damage <b>and</b> ignore DR.'
        elif r in [4,5]: self.critical = 'DR <em>halved</em> <b>and</b> treat a major wound.'
        elif r in [6,7]: self.critical = 'Treat as eye hit (front), or DR <em>halved</em> <b>and</b> treat a major wound (back).'        
        elif r == 8: self.critical = 'Victim must <em>Do Nothing</em> next turn.'    
        elif r in [9,10,11]: self.critical = 'Normal head-blow damage.'
        elif r in [12,13]: self.critical = '<em>If</em> penetrating: cr deafens while other cause severe scarring (-1 Appearance, -2 for burns and cor).'
        elif r in [14]: self.critical = 'Victim <em>drops</em> a weapon.'
        elif r in [15]: self.critical = '<em>Maximum</em> damage.'  
        elif r in [16]: self.critical = '<em>Double</em> damage.' 
        elif r in [17]: self.critical = 'DR <em>halved</em> (round up).'  
        elif r in [18]: self.critical = '<em>Triple</em> damage.'        
        
if __name__ == "__main__":
    # Basic test code for debugging
    test = locator('1','1')
    for i in range(10):
        test.get('imp','Arm Vascular')
