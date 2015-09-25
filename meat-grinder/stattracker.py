# stattracker.py
# -------------------------
# Summer 2013; Christian Blouin & Alex Safatli
# -------------------------
# Library for statistic tracking.

from google.appengine.ext import db

# Database Models

class GrindHit(db.Model):
    realistic = db.BooleanProperty()
    damage_type = db.StringProperty()
    is_random = db.BooleanProperty()
    location = db.StringProperty()
    count = db.IntegerProperty()
    
class Counter(db.Model):
    count = db.IntegerProperty()
    
# Statistic Handling, Gathering

PIECHART_SCRIPT = '''google.setOnLoadCallback(draw$$TITLEF$$);function draw$$TITLEF$$() {
var data = google.visualization.arrayToDataTable([$$DATA$$]);var options = {title: '$$TITLE$$'};
var chart = new google.visualization.PieChart(document.getElementById('$$ID$$'));chart.draw(data, options);}'''

class Gatherer:
    # Saved data.
    saveddata = None
    counts = {'realistic':[0,0],
              'damage_type':{},
              'is_random':[0,0],
              'target_location':{}}
    piecharts = []
    titles = []
    charts = [piecharts]
    
    # Constructor.
    def __init__(self):
        self.__get__()
        self.count()
        
    # Collects the data.
    def __get__(self):
        self.saveddata = GrindHit.all()
        
    # Data processing.
    def count(self):
        counts = self.counts
        
        for item in self.saveddata:
            counts['realistic'][int(item.realistic)] += item.count
            
            if item.damage_type not in counts['damage_type']:
                counts['damage_type'][item.damage_type] = 0
            counts['damage_type'][item.damage_type] += item.count
            
            # Gather stats only on deliberately targetted instead of randomly determined
            if not item.is_random:
                if item.location not in counts['target_location']:
                    counts['target_location'][item.location] = 0
                counts['target_location'][item.location] += item.count
                
            counts['is_random'][int(item.is_random)] += item.count
            
    # Chart creation.
    def addPieChart(self,title,items):
        titlef = title.replace(' ','').replace('.','')
        if titlef in self.titles:
            return # Titles should be unique.
        script = PIECHART_SCRIPT.replace('$$TITLEF$$',titlef)
        script = script.replace('$$TITLE$$',title)
        data = []
        for item in items:
            # Assumes a dictionary.
            data.append("['%s',%s]" % (item,items[item]))
        script = script.replace('$$DATA$$',','.join(data))
        script = script.replace('$$ID$$','chart_%s' % (titlef.lower()))
        self.piecharts.append(script)
        self.titles.append(titlef)
