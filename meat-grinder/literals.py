# literals.py
# -------------------------
# Fall 2015; Alex Safatli
# -------------------------
# String Literals and Value/Probability Tables
# Adapted from GURPS Material

# Types

types = [
         ['cut','Cutting'],
         ['imp','Impaling'],
         ['cr','Crushing'],
         ['pi-','Piercing, Small'],
         ['pi','Piercing, Normal'],
         ['pi+','Piercing, Large'],
         ['pi++','Piercing, Huge'],
         ['aff','Affliction'],
         ['burn','Burning'],
         ['cor','Corrosion'],
         ['fat','Fatigue'],
         ['tox','Toxic']
        ]

# Hit Modifiers

hitmod = {
          'Skull':'-7/-5',
          'Face':'-5/-7',
          'Right Leg':-2,
          'Right Arm':-2,
          'Torso':0,
          'Abdomen':-1,
          'Left Arm':-2,
          'Forearm':-3,
          'Upper Arm':-3,
          'Thigh':-3,
          'Shin':-3,
          'Left Leg':-2,
          'Hand':-4,
          'Foot':-4,
          'Neck':-5,
          'Vitals':-3,
          'Eye':-9,
          'Ear':-7,
          'Nose':-7,
          'Jaw':-6,
          'Spine':-8,
          'Arm Vascular':-5,
          'Leg Vascular':-5,
          'Neck Vascular':-8,
          'Elbow':-5,
          'Knee':-5,
          'Shoulder':-5,
          'Wrist':-7,
          'Ankle':-7,
          'Groin':-3,
          'Pelvis':-3,
          'Digestive Tract':-2,
          'Heart':-5,
          'Cheek':-6
        }

# Using Hit Location & Damage Modifier Table; B552
# http://forums.sjgames.com/showthread.php?t=76205

hit = { 3:'Skull',4:'Skull',5:'Face',6:'Right Leg',
       7:'Right Leg',8:'Right Arm',9:'Torso',
       10:'Torso',11:'Abdomen',12:'Left Arm',
       13:'Left Leg',14:'Left Leg',15:'Hand',
       16:'Foot',17:'Neck',18:'Neck' }

# Using Damage Type and Multipliers Table

mult = { 'aff':None,'burn':1.0,'cor':1.0,'cr':1.0,
       'cut':1.5,'fat':None,'imp':2.0,'pi-':0.5,
       'pi':1.0,'pi+':1.5,'pi++':2.0,'spec':None,
       'tbb':1.0,'tox':1.0 }


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