# main.py
# -------------------------
# Summer 2013; Alex Safatli
# Fall 2015; Alex Safatli
# -------------------------
# Google App Engine Interface with Python Code

import webapp2, jinja2, os, cgi, meatgrinder
from stattracker import Gatherer

# HTML Templating

JINJA_ENVIRONMENT = jinja2.Environment(
    loader = jinja2.FileSystemLoader(
        os.path.dirname(__file__)))

# Main Page Handler

class MainPage(webapp2.RequestHandler):

    # GET /

    def get(self):
    
        # Get parameters from form elements.
        typ = cgi.escape(self.request.get('atktype'))
        loc = cgi.escape(self.request.get('location'))
        realistic = cgi.escape(self.request.get('realistic'))
        facesub = cgi.escape(self.request.get('facesub'))
        
        # Set values in case of empty input.
        if realistic == '': realistic = '0'
        if facesub == '': facesub = '0'
        if not loc: loc = 'random'      
        
        # Remove hit location modifier from string.
        if '(' in loc: loc = ' '.join(loc.split()[-1])
        
        # Set dummy object for hit.
        hit = None
        
        # If a type was provided from input...
        if typ:
            # Instantiate and provide a hit.
            hit = meatgrinder.locator(realistic,facesub)
            hit.get(typ, loc)
            
        # Jinja template value and handling.
        template_values = {'hit':hit,'types':meatgrinder.types, \
                           'parts':meatgrinder.parts,'loc':loc, \
			   'hitmod':meatgrinder.hitmod, 'realistic':realistic, 'facesub':facesub}
        template = JINJA_ENVIRONMENT.get_template('index.html')
        
        # Write to HTML file.
        self.response.write(template.render(template_values))

class StatsHandler(webapp2.RequestHandler):
    def get(self):
    
        # Instantiate and gather statistics from datastore.
        gatherer = Gatherer()
        data = gatherer.counts
        
        # Format data for charts.
        frandom, trandom = data['is_random']
        randomhits = {'':'0','Random Hit':trandom,'Targetted Hit':frandom}
        woreal, wwreal = data['realistic']
        realishits = {'':'0','Hit with Realistic Threshold':wwreal,'Hit without Realistic Threshold':woreal}
        
        # Create pie charts.
        gatherer.addPieChart('Random vs. Targetted Hits',randomhits)
        gatherer.addPieChart('Realistic Hits',realishits)
        gatherer.addPieChart('Targetted Locations',data['target_location'])
        gatherer.addPieChart('Damage Type',data['damage_type'])
        
        # Jinja template value and handling.
        template_values = {'gathered':gatherer}
        template = JINJA_ENVIRONMENT.get_template('./stats/index.html')
        
        # Write to HTML file.
        self.response.write(template.render(template_values))
        
app = webapp2.WSGIApplication([('/', MainPage),('/stats/',StatsHandler),('/stats',StatsHandler)],
                              debug=True)
