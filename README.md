# Catalog Project

This project demonstrates all of the concepts of Full-Stack Development. It includes a set-up for an item catalog, along with the ability for users to add, delete, or edit items.

# Technologies
- Oauth2
- Postgre SQL
- Python Flask
- Bootstrap

This project utilizes the Python Flask framework to deploy my web application via a Vagrant Virtual Host.

I utilized Oauth2 for Gmail Authentication for a user when he logs into the application. They may only make edits to the items that they add, and they will only see the edit and delete buttons if they are the user logged in. Normal viewers will only have the ability to read the item catalog.

I used Postgre SQL to hold my data for the items in the item catalog, with SQL Alchemy to connect this database to Python Flask.

I used Python Flask as the primary resource to help deploy my application into a hosted environment. 

I used Bootstrap for all front-end styling and general look & feel of the web application.

# How to run the project

Place your catalog project in the directory.

In order to begin the project, you must first run the Vagrant Machine.

Make sure you are in the correct directory before starting.

When in the Vagrant Folder, use Vagrant Up and Vagrant SSH to get the VM up and
running.

After Vagrant is ready, CD into the directory /catalog on the Virtual Machine

When CDed, run application.py and report to localhost:8000 on your computer.

There, the functionality should be present.



