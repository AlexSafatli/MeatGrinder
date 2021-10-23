# woundtable.py
# -------------------------
# Summer 2013; Christian Blouin
# -------------------------
# Library for handling wounds for
# meatgrinder.

class WoundInserter:
    def __init__(self, locator):
        # Instance of the locator.
        self.locator = locator

        # What to pass back.
        self.notes = ''

        # Determine type of injury.
        if 'Neck' in locator.location[-1]:
            self.neck_wound()
        elif 'Skull' in locator.location[-1]:
            self.skull_wound()
        elif 'Vascular' in locator.location[-1]:
            self.vascular_wound()
        elif 'Vitals' in locator.location[-1]:
            self.vitals_wound()

        # Pass the data to the locator instance.
        if self.notes:
            self.locator.wound = self.notes

    def get_dice(self):
        return self.locator.roll()

    def neck_wound(self):
        d = self.get_dice()
        if d in [3]:
            self.notes += "Respiratory or circulatory problems, giving -1 HT. " + \
                          "Critical failure on the recovery roll means delayed death by aneurysm. " + \
                          "Treat this as Terminally Ill (up to two years) [p. B158]."
        elif d in [4, 5, 16, 17]:
            self.notes += "Stroke resulting in brain damage. Roll on the " \
                          "Skull Wounds Table for effects. "
            self.skull_wound()
        elif d in [6, 7]:
            self.notes += "Severe neurological damage, resulting in Numb (p. " \
                          "B146). "
        elif d in [14, 15]:
            self.notes += "Damage to the throat, resulting in Disturbing " \
                          "Voice (p. B132) or Cannot " + \
                          "Speak (p. B125), if injured to -HP or worse. "
        elif d == 18:
            self.notes += "Severely reduced neck mobility, giving -1 DX."

    def skull_wound(self):
        d = self.get_dice()
        swt = [3, "Widespread neurological damage, giving Epilepsy (p. B136). ",
               4, "General cognitive impairment, giving -1 IQ. ",
               5,
               "Damage to the prefrontal cortex, giving Low Empathy (p. B142). ",
               6,
               "Damage to the temporal lobes, giving Partial Amnesia (p. B123) or "
               "Total Amnesia, if injured to -HP or worse. ",
               7, "Damage to the parietal lobe, giving Dyslexia (p. B134). ",
               8,
               "Damage to the cerebellum, giving slurred speech. Treat this as Stuttering (p. B157). ",
               9,
               "Damage to the occipital lobes, giving Bad Sight (p. B123). Critical failure on the recovery roll means Blindness (p. B124)! ",
               12,
               "Ruptured eardrums or damage to the temporal lobe, giving Hard of Hearing (p. B138). Critical failure on the recovery roll means full Deafness (p. B129). ",
               13,
               "Damage to the cerebellum, giving a level of Ham-Fisted (p. B138), or two levels if injured to -HP or worse. ",
               14,
               "Widespread brain damage, giving Neurological Disorder(Mild). See p. B144. ",
               15,
               "Brain stem damage that impairs reaction time (startle response), giving -1 Basic Speed. ",
               16, "Severe damage to the cerebellum, giving -1 DX. ",
               17,
               "Widespread brain damage, giving Neurological Disorder (Severe). ",
               18,
               "Widespread brain damage, giving Neurological Disorder (Crippling). "]

        if d in swt:
            self.notes += swt[swt.index(d) + 1]

    def vascular_wound(self):
        d = self.get_dice()
        if d in [3]:
            self.notes += "Circulatory damage, giving -1 HT. Critical failure " + \
                          "on the recovery roll means delayed death resulting " + \
                          " from aneurysm. Treat this as Terminally Ill (Up " + \
                          "to two years); see p. B158. "
        elif d in [4, 5, 16, 17]:
            self.notes += "For an artery in the arm or leg, lack of blood " + \
                          "flow cripples the limb; treat this as a crippled " + \
                          "limb. "
            if 'Neck' in self.locator.location[0]:
                self.neck_wound()
        elif d in [6, 7]:
            self.notes += "Circulatory damage, giving one level of Easy " + \
                          "to Kill (p. B134) plus one extra level if injured " + \
                          "to -HP, two extra levels at -2 HP, and so on. "
        elif d in [14, 15]:
            self.notes += "A severe tear that counts as Wounded (p. B162). " + \
                          "This can become permanent, like any other " + \
                          "crippling injury. "
        elif d == 18:
            self.notes += "A blood clot travels to the brain and causes a " + \
                          "stroke. Roll on the Skull Wounds Table for effects. "
            self.skull_wound()

    def vitals_wound(self):
        d = self.get_dice()
        vmw = [3,
               "Severely weakened vital organ(s), giving -1 HT. Critical "
               "failure on the recovery roll means eventual death due to "
               "organ failure. Treat this as Terminally Ill (up to two "
               "years); see p. B158. ",
               4,
               "Stabbing pains in the chest or abdomen that count as Chronic "
               "Pain (p. B126). The GM assesses effects worth roughly -1 "
               "point per lost HP. For instance, 21 HP of injury might cause "
               "Chronic Pain (Agonizing; 4 hours; 9 or less) [-22]. ",
               5,
               "Damage to the kidneys, liver, pancreas, or other organs, "
               "resulting in Restricted  Diet (p. B151). The special "
               "diet amounts to a very common item. ",
               6,
               "Shock  to  the  immune  system,  giving  one  level  of "
               "Susceptible to Disease (p. B158) plus one extra level if "
               "injured to -HP, two extra levels at -2 HP, and so on. ",
               7,
               "Reduced  cardiovascular  fitness,  giving  -1  FP  plus  an "
               "extra -1 FP if injured to -HP, -2 FP at -2 HP, and so on. ",
               8,
               "Weakened  heart,  giving  one  level  of  Easy  to  Kill (p. "
               "B134) plus one extra level if injured to -HP, two extra "
               "levels at -2HP, and so on. ",
               13,
               "A deep hole that counts as Wounded (p. B162). If this becomes "
               "permanent, it may be deliberate (a result of surgery) or the "
               "result of incomplete healing. ",
               14,
               "General damage to the vital organs, leading to Slow Healing 1 "
               "(p. B155). ",
               15,
               "Severely  reduced  cardiovascular  health,  giving  Unfit(p. "
               "B160) or Very Unfit, if injured to -4HP or worse. ",
               16,
               "Chronic health problems that require daily care. Treat as "
               "Maintenance (Physician; 1 person; Daily); see p. B142. ",
               17,
               "Chronic health problems that requires care three times per "
               "day. Treat as Maintenance (Physician; 1 person; Three times "
               "daily). ",
               18,
               "Chronic health problems that requires constant life support. "
               "Treat as Maintenance (Physician; 1 person; Constant). "]

        if d in vmw:
            self.notes += vmw[vmw.index(d) + 1]
