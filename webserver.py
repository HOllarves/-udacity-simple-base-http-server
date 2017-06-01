import cgi
import os
import jinja2
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

template_dir = os.path.join(os.path.dirname(__file__), 'views')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),  autoescape = True)

# Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class webServerHandler(BaseHTTPRequestHandler):

    # Data methods
    def getAllRestaurants(self):
        restaurants = session.query(Restaurant).all()
        return restaurants

    def getRestaurant(self, id):
        restaurant = session.query(Restaurant).filter_by(id = id).one()
        return restaurant

    # Outputs to the browser
    def write(self, *args, **kwargs):
        self.wfile.write(*args, **kwargs)

    # Looks for template and add params
    def render_str(self, template, **params):
        t = jinja_env.get_template(template)
        return t.render(params)

    # Renders the template
    def render(self, template, **kwargs):
        self.write(self.render_str(template, **kwargs))

    def do_GET(self):
        try:
            if self.path.endswith('/'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                restaurants = self.getAllRestaurants()
                self.render('list.html', restaurants=restaurants)
                return

            if self.path.endswith('/new'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                self.render('new.html')
                return

            if self.path.endswith('/edit'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                restaurant_id = self.path.split('/')[1]
                restaurant = self.getRestaurant(restaurant_id)
                self.render('edit.html', restaurant=restaurant)

            if self.path.endswith('/delete'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                restaurant_id = self.path.split('/')[1]
                restaurant = self.getRestaurant(restaurant_id)
                self.render('delete.html', restaurant=restaurant)

        except IOError:
            self.send_error(404, "File not found %s" % self.path)

    def do_POST(self):
        try:
            if self.path.endswith('/new'):
                self.send_response(301)
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    postvars = cgi.parse_multipart(self.rfile, pdict)
                    new_restaurant = Restaurant(name=postvars['name'][0])
                    session.add(new_restaurant)
                    session.commit()
                    self.send_header('Location', '/')
                elif ctype == 'application/x-www-form-urlencoded':
                    length = int(self.headers.getheader('content-length'))
                    postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
                    new_restaurant = Restaurant(name=postvars['name'][0])
                    session.add(new_restaurant)
                    session.commit()
                    self.send_header('Location', '/')
                else:
                    postvars = None
                    return
                self.end_headers()
                return
            if self.path.endswith('/edit'):
                self.send_response(301)
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    postvars = cgi.parse_multipart(self.rfile, pdict)
                    old_restaurant = self.getRestaurant(postvars['id'][0])
                    old_restaurant.name = postvars['name'][0]
                    session.add(old_restaurant)
                    session.commit()
                    self.send_header('Location', '/')
                elif ctype == 'application/x-www-form-urlencoded':
                    length = int(self.headers.getheader('content-length'))
                    postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
                    old_restaurant = self.getRestaurant(postvars['id'][0])
                    old_restaurant.name = postvars['name'][0]
                    session.add(old_restaurant)
                    session.commit()
                    self.send_header('Location', '/')
                    return
                return
            if self.path.endswith('/delete'):
                self.send_response(301)
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    postvars = cgi.parse_multipart(self.rfile, pdict)
                    restaurant = self.getRestaurant(postvars['id'][0])
                    session.delete(restaurant)
                    session.commit()
                    self.send_header('Location', '/')
                elif ctype == 'application/x-www-form-urlencoded':
                    length = int(self.headers.getheader('content-length'))
                    postvars = cgi.parse_qs(self.rfile.read(length), keep_blank_values=1)
                    restaurant = self.getRestaurant(postvars['id'][0])
                    session.delete(restaurant)
                    session.commit()
                    self.send_header('Location', '/')
                    return
                return
        except:
            self.send_error(500, "Internal Server Error")



def main():
    try:
        port = 8080
        server = HTTPServer(('', port), webServerHandler)
        print "Web server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print "^C entered, stopping web server..."
        server.socket.close()

if __name__ == '__main__':
    main()