# Base HTTPServer



This is a simple implementation of Python's Base HTTPServer for anyone who needs some help setting up their own.

In this small project, I created a simple API with CRUD operations for restaurants.

This project was built inside a Vagrant Virtual Machine running Ubuntu.

To start server, simply `python webserver`

This will start a webserver at port 8080. For data persistence, I used SQLite.
For data communication, SQLAlchemy ORM was implemented to communicate with our database.
Lastly, Jinja2 was used as a template engine (although this templates are **very very** ugly)


