#!/usr/bin/env python2.7
import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, make_response, flash

from models import entrants, residents, service_providers, guests, admins, vehicles

tmpl_dir = os.path.join(
    os.path.dirname(
        os.path.abspath(__file__)),
    'templates')
app = Flask(__name__, template_folder=tmpl_dir)


# The following is a dummy URI that does not connect to a valid database. You
# will need to modify it to connect to your Part 2 database in order to use the
# data.
#
# The URI should be in the format of:
#
#     postgresql://USER:PASSWORD@w4111a.eastus.cloudapp.azure.com/proj1part2

DBURI = 'postgresql://mag2272:C9qlubhnlN@w4111a.eastus.cloudapp.azure.com/proj1part2'
engine = create_engine(DBURI)


@app.before_request
def before_request():
    """
    This function is run at the beginning of every web request (every time you
    enter an address in the web browser).  We use it to setup a database
    connection that can be used throughout the request.

    The variable g is globally accessible.
    """
    try:
        g.conn = engine.connect()

        user_id = request.cookies.get('user_id')
        entity_type = request.cookies.get('entity_type')

        if user_id is None or entity_type is None:
            g.user_id = None
            g.entity_type = None
        elif entity_type == 'residents':
            if residents.find_by_id(user_id, g.conn) is None:
                return redirect('/')
        elif entity_type == 'businesses':
            if service_providers.find_by_id(user_id, g.conn) is None:
                return redirect('/')
        elif entity_type == 'admins':
            admin = admins.find_by_id(user_id, g.conn)
            if admin is None:
                return redirect('/')
            g.building_id = admin.building_id
        else:
            g.user_id = None
            g.entity_type = None
            return redirect('/')

        g.user_id = user_id
        g.entity_type = entity_type

    except:
        print "uh oh, problem connecting to database"
        import traceback
        traceback.print_exc()
        g.conn = None


@app.teardown_request
def teardown_request(exception):
    """
    At the end of the web request, this makes sure to close the database
    connection.  If you don't, the database could run out of memory!
    """
    try:
        g.conn.close()
    except Exception as e:
        pass


@app.route('/')
def index():
    """
    request is a special object that Flask provides to access web request
    information:

    request.method:   "GET" or "POST" request.form:     if the browser submitted
    a form, this contains the data in the form request.args:     dictionary of
    URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

    See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
    """
    return render_template('home.html')


@app.route('/another')
def another():
    return render_template("another.html")

# Example of adding new data to the database


@app.route('/add', methods=['POST'])
def add():
    name = request.form['name']
    g.conn.execute('INSERT INTO test(name) VALUES (%s)', name)
    return redirect('/')


@app.route('/login/<entity_type>', methods=['GET', 'POST'])
def login(entity_type):
    if g.user_id and g.entity_type:
        if g.entity_type == 'businesses':
            return redirect('/{}/business_dashboard'.format(g.user_id))
        elif g.entity_type == 'residents':
            return redirect('/resident_dashboard/{}'.format(g.user_id))
        elif g.entity_type == 'admins':
            return redirect('/admin_dashboard/{}'.format(g.user_id))


    if entity_type == 'residents':
        if request.method == 'POST':
            username = request.form.get('username')
            resident = (residents.find_by_username(username, g.conn)
                        if username else None)
            if resident:
                resp = make_response(
                        redirect('/resident_dashboard/{}'.format(
                            resident.entrant_id)))
                resp.set_cookie('user_id', value=str(resident.entrant_id))
                resp.set_cookie('entity_type', entity_type)
                return resp

    elif entity_type == 'admins':
        if request.method == 'POST':
            username = request.form.get('username')
            admin = (admins.find_by_username(username, g.conn)
                     if username else None)
            if admin:
                resp = make_response(
                        redirect('/admin_dashboard/{}'.format(admin.entrant_id)))
                resp.set_cookie('user_id', value=str(admin.entrant_id))
                resp.set_cookie('entity_type', entity_type)
                return resp

    elif entity_type == 'businesses':
        if request.method == 'POST':
            email = request.form.get('username')
            business = (service_providers.find_by_email(email, g.conn)
                        if email else None)
            if business:
                resp = make_response(
                        redirect('/{}/business_dashboard'.format(
                            business.business_id)))
                resp.set_cookie('user_id', value=str(business.business_id))
                resp.set_cookie('entity_type', entity_type)
                return resp

    return render_template('login.html', entity_type=entity_type)

@app.route('/logout')
def logout():
    resp = make_response(redirect('/'))
    resp.set_cookie('user_id', '', expires=0)
    resp.set_cookie('entity_type', '', expires=0)
    return resp

@app.route('/admin_dashboard/<admin_id>')
def route_to_search(admin_id):
    return redirect('/admin_dashboard/{}/search'.format(admin_id))

@app.route('/admin_dashboard/<admin_id>/<dash_type>', methods=['GET', 'POST'])
def admin_dashboard(admin_id, dash_type):
    if g.entity_type != 'admins' or g.user_id != admin_id:
        return redirect('/')

    admin = admins.find_by_id(g.user_id, g.conn)

    if dash_type == 'search':
        search_results = []
        if request.method == 'POST':
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            search_results = entrants.search_by_name(
                    fname, lname, admin.building_id, g.conn)
        return render_template(
                'admin_dashboard_search.html',
                admin=admin,
                results=search_results)

    if dash_type == 'requested_cars':
        if request.method == 'POST': # Unpark the car in the get params
            state_of_car_to_unpark = request.args.get('ups')
            pnum_of_car_to_unpark  = request.args.get('upl')

            unpark_car(admin.building_id, state_of_car_to_unpark, pnum_of_car_to_unpark)

        cars = vehicles.find_requested_cars(g.conn, admin.building_id)
        map(lambda c: c.get_drivers(g.conn), cars)
        return render_template('requested_cars.html', cars=cars, admin=admin)

    if dash_type == 'park':
        if request.method == 'POST':
            state = request.form.get('state')
            pnum = request.form.get('pnum')
            res = vehicles.find_by_license_plate(g.conn, state, pnum)
            if res is not None:
                return redirect(
                        '/admin_dashboard/{}/edit_car?s={}&l={}'.format(
                            admin.entrant_id,
                            state,
                            pnum))
            else:
                return redirect(
                        '/admin_dashboard/{}/add_car?s={}&l={}'.format(
                            admin.entrant_id,
                            state,
                            pnum))

        return render_template('admin_dashboard_park.html', admin=admin)

    if dash_type == 'add_car':
        state = request.args.get('s')
        pnum = request.args.get('l')
        if request.method == 'POST':
            kwargs = { attr:val if val else None
                       for attr, val in request.form.iteritems()}
            kwargs['is_requested'] = False
            kwargs['building_id'] = admin.building_id
            kwargs['state'] = state
            kwargs['plate_num'] = pnum
            new_car = vehicles(**kwargs)
            new_car.put(g.conn)
            return redirect(
                        '/admin_dashboard/{}/edit_car?s={}&l={}'.format(
                            admin.entrant_id,
                            state,
                            pnum))
        return render_template(
                'add_car.html', admin=admin, state=state, pnum=pnum)

    if dash_type == 'edit_car':
        state = request.args.get('s')
        pnum = request.args.get('l')
        if request.method == 'POST':
            try:
                update_car(state, pnum, request, admin.building_id)
            except:
                flash('Error: Default parking spot is taken.')

            try:
                park_car(state, pnum, request, admin.building_id)
            except:
                flash('Error: Spot is taken, key slot is taken, or spot does not exist.')
        car = vehicles.find_by_license_plate(g.conn, state, pnum)
        if car is None:
            return redirect('/')
        return render_template('edit_car.html', car=car, admin=admin)


@app.route('/resident_dashboard/<user_id>')
def route_to_guests(user_id):
    return redirect('/resident_dashboard/{}/guests'.format(user_id))

@app.route('/resident_dashboard/<user_id>/<dash_type>', methods=['GET', 'POST'])
def display_dashboard(user_id, dash_type):
    if g.entity_type != 'residents' or g.user_id != user_id:
        return redirect('/')
    resident = residents.find_by_id(user_id, g.conn)

    if dash_type == 'guests':
        if request.method == 'POST':
            for guest_id, _ in request.form.iteritems():
                guests.delete_by_id(guest_id, g.conn)
        guests_of_resident = resident.get_guests(g.conn)
        return render_template(
                'resident_dashboard_guests.html',
                resident=resident,
                guests=guests_of_resident,
                entity_type="Resident")

    elif dash_type == 'add_guests':
        if request.method == 'POST':
            fname = request.form.get('fname')
            lname = request.form.get('lname')
            new_guest = guests(
                    building_id=resident.building_id,
                    unit_id=resident.unit_id,
                    fname=fname,
                    lname=lname)
            new_guest.put(g.conn)
            flash('Guest successfully added: {} {}'.format(fname, lname))
        return render_template(
                'resident_dashboard_add_guests.html',
                resident=resident)

    elif dash_type == 'cars':
        cars = resident.get_cars(g.conn)
        if request.method == 'POST':
            for car in cars:
                car_identifier = '{} {}'.format(car.plate_num, car.state)
                if car_identifier in request.form and not car.is_requested:
                    car.request(g.conn)
                elif car_identifier not in request.form and car.is_requested:
                    car.request(g.conn, False)
        map(lambda c: c.get_drivers(g.conn), cars)
        return render_template(
                'resident_dashboard_cars.html',
                resident=resident,
                cars=cars,
                entity_type="Resident")

    elif dash_type == 'services':
        services = service_providers.list_for_building(resident.building_id, g.conn)

        return render_template(
            'resident_dashboard_services.html',
            resident=resident,
            services=services)

    return redirect('/')

@app.route('/car/<state>/<license_plate>/', methods=['GET', 'POST'])
def car(state, license_plate):
    if g.entity_type != 'admins':
        return redirect('/')

    admin = admins.find_by_id(g.user_id, g.conn)

    car = vehicles.find_by_license_plate(g.conn, state, license_plate)

    if(car != None):
        return render_template('edit_car.html', car=car, admin=admin)
    else:
        return render_template(
                'error.html', error_desc="That car was not found.", admin=admin)

def update_car(state, license_plate, request, building_id):
    # Update the database based on the form data
    g.conn.execute(
        'UPDATE vehicles\
         SET make = \'' + request.form["make"] + '\'\
         WHERE state = \'' + str(state) + '\' AND plate_num = \'' + str(license_plate) + '\'')

    g.conn.execute(
        'UPDATE vehicles\
         SET model = \'' + request.form["model"] + '\'\
         WHERE state = \'' + str(state) + '\' AND plate_num = \'' + str(license_plate) + '\'')

    g.conn.execute(
        'UPDATE vehicles\
         SET color = \'' + request.form["color"] + '\'\
         WHERE state = \'' + str(state) + '\' AND plate_num = \'' + str(license_plate) + '\'')

    try:
        if(request.form["default_spot"] != None and request.form["default_spot"] != ""):

            spot_cursor = g.conn.execute(
                '''SELECT spot_type
                 FROM parking_spots
                 WHERE building_id = {} AND spot_number = {} AND spot_type = 'Permanent' '''.format(building_id, request.form["default_spot"]))

            if(spot_cursor.fetchone() != None):
                g.conn.execute(
                    'UPDATE vehicles\
                     SET default_spot = \'' + request.form["default_spot"] + '\'\
                     WHERE state = \'' + str(state) + '\' AND plate_num = \'' + str(license_plate) + '\'')
            else:
                flash("Cannot set default parking spot as {}. It does not exist, or it is not a permanent spot.".format(request.form["default_spot"]))
        else:
            g.conn.execute(
                'UPDATE vehicles\
                 SET default_spot = NULL \
                 WHERE state = \'' + str(state) + '\' AND plate_num = \'' + str(license_plate) + '\'')
    except:
        raise

def park_car(state, license_plate, request, building_id):
    # TODO: park the car only for this building
    if(request.form["spot_number"] != None and request.form["spot_number"] != "" and request.form["key_number"] != None and request.form["key_number"] != ""):
        g.conn.execute(
            'UPDATE vehicles\
             SET spot_number = \'' + request.form["spot_number"] + '\', key_number = \'' + request.form["key_number"] + '\'\
             WHERE building_id = ' + str(building_id) + ' AND state = \'' + str(state) + '\' AND plate_num = \'' + str(license_plate) + '\'')

@app.route('/add_car', methods=['GET', 'POST'])
def add_car():
    if g.entity_type != 'admin':
        return redirect('/')
    admin = admins.find_by_id(g.user_id, g.conn)

    if request.method == 'POST':

        new_car = ()

        # TODO: set building ID of car to current building
        if(request.form["spot_number"] != None and request.form["spot_number"] != "" and request.form["key_number"] != None and request.form["key_number"] != ""):
            g.conn.execute(
                'UPDATE vehicles\
                 SET spot_number = \'' + request.form["spot_number"] + '\'\
                 WHERE state = \'' + str(state) + '\' AND plate_num = \'' + str(license_plate) + '\'')
            g.conn.execute(
                'UPDATE vehicles\
                 SET key_number = \'' + request.form["key_number"] + '\'\
                 WHERE state = \'' + str(state) + '\' AND plate_num = \'' + str(license_plate) + '\'')

        return redirect('/car/' + state + '/' + license_plate)

    return render_template('add_car.html', admin=admin)

def unpark_car(building_id, state, plate_num):
    g.conn.execute(
                'UPDATE vehicles\
                 SET spot_number = NULL, key_number = NULL, is_requested = FALSE \
                 WHERE building_id = ' + str(building_id) + ' AND state = \'' + str(state) + '\' AND plate_num = \'' + str(plate_num) + '\'')

@app.route('/<int:provider_id>/business_dashboard', methods=['GET', 'POST'])
def business_dashboard(provider_id):
    if g.user_id != str(provider_id) or g.entity_type != 'businesses':
        return redirect('/')

    if request.method == 'POST':

        # Update the database based on the form data
        g.conn.execute(
            'UPDATE service_providers\
             SET business_description = \'' + request.form["description"] + '\'\
             WHERE business_id = ' + str(provider_id))

        g.conn.execute(
            'UPDATE service_providers\
             SET email = \'' + request.form["email"] + '\'\
             WHERE business_id = ' + str(provider_id))

        g.conn.execute(
            'UPDATE service_providers\
             SET phone_num = \'' + request.form["phone_num"] + '\'\
             WHERE business_id = ' + str(provider_id))

        # Clear the serviced buildings for this particular business
        g.conn.execute(
            'DELETE FROM ONLY provides_services_for AS psf\
             WHERE psf.business_id = ' + str(provider_id))

        # Add the selected buildings to the list of buildings that this business services
        for serviced_building in request.form.getlist("building"):
            g.conn.execute(
                'INSERT INTO provides_services_for (business_id, building_id) VALUES\
                 (' + str(provider_id) + ", " + str(serviced_building) + ")")

    # Verify that we are logged in as a service provider.
    business_cursor = g.conn.execute(
        'SELECT sp.business_id, sp.business_name, sp.business_description, sp.phone_num, sp.email \
         FROM service_providers sp \
         WHERE sp.business_id = ' + str(provider_id))

    business = business_cursor.fetchone()

    if (business != None):
        buildings_cursor = g.conn.execute(
            'SELECT buildings.building_name, buildings.building_id \
             FROM buildings')

        buildings = []

        for record in buildings_cursor:

            check_service_cursor = g.conn.execute(
                'SELECT psf.business_id, psf.building_id \
                 FROM provides_services_for psf \
                 WHERE psf.business_id = ' 
                + str(business.business_id) + "AND psf.building_id = " + str(record.building_id))

            building_entry = dict(record)

            if(check_service_cursor.fetchone() != None):
                building_entry['service_available'] = "checked"
            else:
                building_entry['service_available'] = ""

            buildings.append(building_entry)

        cur_description = "This is the description currently in the database."
        return render_template('business_dashboard.html', buildings=buildings, business=business)
    else:
        return render_template('error.html', error_desc="This user is not a business.")

if __name__ == "__main__":
    import click

    @click.command()
    @click.option('--debug', is_flag=True)
    @click.option('--threaded', is_flag=True)
    @click.argument('HOST', default='0.0.0.0')
    @click.argument('PORT', default=8111, type=int)
    def run(debug, threaded, host, port):
        """
        This function handles command line parameters.
        Run the server using:

            python server.py

        Show the help text using:

            python server.py --help

        """

        HOST, PORT = host, port
        print "running on %s:%d" % (HOST, PORT)
        app.secret_key = "such a clever key"
        app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

    run()
