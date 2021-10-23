from flask import Blueprint, render_template
from webargs import fields
from webargs.flaskparser import use_args

from meatgrinder import engine

blueprint = Blueprint('meatgrinder', __name__, template_folder='templates')


@blueprint.route('/')
@use_args({'atktype': fields.Str(), 'location': fields.Str(),
           'realistic': fields.Str(), 'facesub': fields.Str()},
          location='query')
def home(query_args):
    typ = query_args['atktype'] if 'atktype' in query_args else ''
    loc = query_args['location'] if 'location' in query_args else ''
    realistic = query_args['realistic'] if 'realistic' in query_args else ''
    facesub = query_args['facesub'] if 'facesub' in query_args else ''

    if realistic == '':
        realistic = '0'
    if facesub == '':
        facesub = '0'
    if not loc:
        loc = 'random'

    # Remove hit location modifier from string.
    if '(' in loc:
        loc = ' '.join(loc.split()[-1])

    # Set dummy object for hit.
    hit = None

    if typ:
        hit = engine.HitLocation(realistic, facesub)
        hit.get(typ, loc)

    # Jinja template value and handling.
    template_values = {'hit': hit, 'types': engine.types,
                       'parts': engine.parts, 'loc': loc,
                       'hitmod': engine.hitmod, 'realistic': realistic,
                       'facesub': facesub}

    return render_template('index.html', **template_values)
