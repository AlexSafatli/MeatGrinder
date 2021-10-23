# meatgrinder.py
# -------------------------
# Summer 2013; Alex Safatli/Christian Blouin
# -------------------------
# API for handling hit location
# determination using GURPS rules.

from random import choice

from meatgrinder import notetable, woundtable
from meatgrinder.rng import Dice
from meatgrinder.literals import *

parts = list(notetable.notes.keys())
parts.sort()


class HitLocation:
    def __init__(self, realistic: str, facesub: str):
        self.location = None
        self.atktype: str = ''

        # Damage multiplier (float).
        self.multiplier = 1.0

        # General message to pass to user (list of strings).
        self.notes = []

        # Map of thresholds appropriate for location (dictionary of strings).
        self.threshold = None

        # If a wound were to occur, what would happen (string).
        self.wound = None

        # Dice roller instances.
        self.dice = Dice(3, 6)  # 3d6
        self.die = Dice(1, 6)  # 1d6

        # Determine realistic, facesub filters.
        self.realistic = '1' in realistic
        self.facesub = '1' in facesub

    def _get_loc(self, location: str):
        if location == 'random':
            self.location = (hit[self.roll()],)
        else:
            self.location = (location,)

    def get(self, atktype: str, location: str):
        self.atktype = atktype
        self._get_loc(location)

        # Set multiplier
        if atktype in mult:
            self.multiplier = mult[atktype]

        # Handle thresholds and sublocations
        loc = self.location[0]
        rl = self.die.roll()

        # Low Tech Hit
        if loc in ['Arm', 'Leg']:
            r2 = self.die.roll()
            # Arm
            if 'Arm' in loc:
                if r2 <= 3:
                    self.location = (loc, 'Forearm')
                elif r2 == 4:
                    self.location = (loc, 'Elbow')
                elif r2 == 5:
                    self.location = (loc, 'Upper Arm')
                elif r2 == 6:
                    self.location = (loc, 'Shoulder')
                # Leg
            if 'Leg' in loc:
                if r2 <= 3:
                    self.location = (loc, 'Shin')
                elif r2 == 4:
                    self.location = (loc, 'Knee')
                elif r2 > 4:
                    self.location = (loc, 'Thigh')
        elif loc in ['Shin', 'Knee', 'Thigh']:
            self.location = ('Leg', loc)
            loc = 'Leg'
        elif loc in ['Forearm', 'Elbow', 'Upper Arm', 'Shoulder']:
            self.location = ('Arm', loc)
            loc = 'Arm'

        if rl == 1:  # Roll of 1.
            # Arm or leg.
            if 'Vascular' not in loc and ('Arm' in loc or
                                          'Leg' in loc) and not (
                    'cr' in atktype):  # Vascular Hit
                # Get Side
                side = loc.split()[0]
                chunk = 'Arm' if ('Arm' in loc) else 'Leg'

                # Reformat locs
                if len(loc.split()) == 1 or chunk in self.location[-1]:
                    self.location = (self.location[-1], '%s Vascular' % chunk)
                else:
                    self.location = (side + ' ' + self.location[-1],
                                     '%s Vascular' % chunk)

            # In the face.
            elif 'Face' in loc:
                self.location = (loc, 'Skull' if (atktype in
                                                  ['imp', 'burn'] or 'pi' in
                                                  atktype) else 'Nose')

            # Hand or feet.
            elif atktype in ['cr', 'cut', 'burn'] or 'pi' in atktype and (
                    'Hand' in loc or 'Foot' in loc):
                self.location = (choice(['Left', 'Right']) + ' ' + loc,
                                 'Wrist' if ('Hand' in loc) else 'Ankle')

            # Neck or torso.
            elif atktype in ['cut', 'imp', 'burn'] or 'pi' in atktype and (
                    'Neck' in loc or 'Torso' in loc):
                self.location = (loc,
                                 'Neck Vascular' if (
                                         'Neck' in loc) else 'Vitals')

        # Abdomen
        if 'Abdomen' == loc:
            if rl == 1:
                self.location = (loc, 'Vitals')
            elif rl <= 4:
                self.location = (loc, 'Digestive Tract')
            elif rl == 5:
                self.location = (loc, 'Pelvis')
            else:
                self.location = (loc, 'Groin')

        # Face sub-location (when not already resolved).
        if self.facesub and 'Face' == loc and len(self.location) == 1:
            r1 = self.die.roll()
            if r1 == 1:
                self.location = (loc, 'Jaw')
            elif r1 == 2:
                self.location = (loc, 'Nose')
            elif r1 == 3:
                self.location = (loc, 'Ear')
            elif r1 == 4 or r1 == 5:
                self.location = (loc, 'Cheek')
            else:
                self.location = (loc, 'Eye')

        # Set threshold dictionary; order.
        self.set_threshold()

        # Process notes, wounds
        notetable.NoteInserter(self)
        woundtable.WoundInserter(self)

        # Process critical hits
        if loc in ['Face', 'Skull', 'Eye', 'Ear', 'Nose', 'Cheek', 'Jaw']:
            self.critical_hit_on_head()
        else:
            self.critical_hit()

    def roll(self):
        return self.dice.roll()

    def set_threshold(self):
        fal = 'for any action involving that location'
        if self.realistic:
            arminj = [
                ['1 HP and more', '-1 DX %s (incl. two-handed tasks).' % (fal)],
                ['over HP/5, up to HP/3',
                 '-3 DX %s (incl. two-handed tasks).' % (fal)],
                ['over HP/3, up to HP/2',
                 'The arm is almost broken; Will roll to use; success at -5 DX.']]
            leginj = [['more than 1 HP',
                       '-1 DX %s and with good leg if standing.' % (fal)],
                      ['over HP/5, up to HP/3',
                       '-3 DX %s and -1 with good leg if standing.' % (fal)],
                      ['over HP/3, up to HP/2',
                       'The leg is almost broken; Will roll to use.']]
            torsod = [['1 HP and more', '-1 DX for all purposes.'],
                      ['over HP/2', '-2 DX Movement is 80% of normal.'],
                      ['over 2/3HP', '-3 DX. Movement is 50% of normal.']]
        else:
            arminj = []
            leginj = []
            torsod = None

        # Extremites
        quarinj = [['over HP/3', 'Crippled'], ['twice crippled', 'Severed']]

        # Joints
        jextre = [['over HP/4', 'Crippled'], ['twice crippled', 'Severed']]

        # Build full dictionary
        inj = {'Right Arm': arminj, 'Left Arm': arminj, 'Arm': arminj,
               'Right Leg': leginj, 'Left Leg': leginj, 'Leg': arminj,
               'Eye': [['over HP/10', 'Blinded'],
                       ['twice blinded', 'Destroyed']],
               'Right Hand': quarinj, 'Left Hand': quarinj, 'Hand': quarinj,
               'Right Foot': quarinj, 'Left Foot': quarinj, 'Foot': quarinj,
               'Nose': jextre, 'Spine': [['over HP', 'Crippled']],
               'Torso': torsod}

        for side in ['Left', 'Right']:
            for part in ['Forearm', 'Upper Arm']:
                inj[side + ' ' + part] = arminj + [['over HP/2', 'Crippled'],
                                                   ['twice crippled',
                                                    'Severed']]
                inj[part] = arminj + [['over HP/2', 'Crippled'],
                                      ['twice crippled', 'Severed']]
            for part in ['Elbow', 'Shoulder']:
                inj[side + ' ' + part] = arminj[:-1] + [
                    ['over HP/3', 'Crippled'], ['twice crippled', 'Severed']]
                inj[part] = arminj[:-1] + [['over HP/3', 'Crippled'],
                                           ['twice crippled', 'Severed']]
            for part in ['Shin', 'Thigh']:
                inj[side + ' ' + part] = leginj + [['over HP/2', 'Crippled'],
                                                   ['twice crippled',
                                                    'Severed']]
                inj[part] = leginj + [['over HP/2', 'Crippled'],
                                      ['twice crippled', 'Severed']]
            for part in ['Knee']:
                inj[side + ' ' + part] = leginj[:-1] + [
                    ['over HP/3', 'Crippled'], ['twice crippled', 'Severed']]
                inj[part] = leginj[:-1] + [['over HP/3', 'Crippled'],
                                           ['twice crippled', 'Severed']]
            for part in ['Ankle', 'Wrist']:
                inj[side + ' ' + part] = [['over HP/4', 'Crippled'],
                                          ['twice crippled', 'Severed']]
                inj[part] = [['over HP/4', 'Crippled'],
                             ['twice crippled', 'Severed']]

        loc = self.location[-1]
        if loc in inj:
            self.threshold = inj[loc]
        if self.threshold is None:
            self.threshold = [['over HP/2', 'Major Wound']]

    # Critical Hit
    def critical_hit(self):
        r = self.roll()
        if r in [3, 18]:
            self.critical = '<em>Triple</em> damage.'
        elif r in [4, 17]:
            self.critical = 'DR <em>halved</em>.'
        elif r in [5, 16]:
            self.critical = '<em>Double</em> damage.'
        elif r in [6, 15]:
            self.critical = '<em>Maximum</em> damage.'
        elif r in [7, 13, 14]:
            self.critical = 'Major injury <em>if</em> penetrating damage.'
        elif r in [8]:
            self.critical = '<em>Funny bone</em>: double shock, extremities crippled for 16-HT turns.'
        elif r in [12]:
            self.critical = 'Victim <em>drops</em> something.'
        else:
            self.critical = 'No active defense allowed.'

    # Critical head injuries
    def critical_hit_on_head(self):
        r = self.roll()
        if r == 3:
            self.critical = '<em>Maximum</em> damage <b>and</b> ignore DR.'
        elif r in [4, 5]:
            self.critical = 'DR <em>halved</em> <b>and</b> treat a major wound.'
        elif r in [6, 7]:
            self.critical = 'Treat as eye hit (front), or DR <em>halved</em> <b>and</b> treat a major wound (back).'
        elif r == 8:
            self.critical = 'Victim must <em>Do Nothing</em> next turn.'
        elif r in [9, 10, 11]:
            self.critical = 'Normal head-blow damage.'
        elif r in [12, 13]:
            self.critical = '<em>If</em> penetrating: cr deafens while other cause severe scarring (-1 Appearance, -2 for burns and cor).'
        elif r in [14]:
            self.critical = 'Victim <em>drops</em> a weapon.'
        elif r in [15]:
            self.critical = '<em>Maximum</em> damage.'
        elif r in [16]:
            self.critical = '<em>Double</em> damage.'
        elif r in [17]:
            self.critical = 'DR <em>halved</em> (round up).'
        elif r in [18]:
            self.critical = '<em>Triple</em> damage.'


if __name__ == "__main__":
    # Basic test code for debugging
    test = HitLocation('1', '1')
    for i in range(10):
        test.get('imp', 'Arm Vascular')
