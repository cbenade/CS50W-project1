# Project 1 Summary
My Project 1 assignment is a simple book review website that uses both information from a local database along with data from the Goodreads API to provide a pleasant and simple user experience for users wishing to submit or read reviews for various books.

Though users are required to register and login before viewing the sites main features, an API route has been created for developers wishing to recieve JSON packages of data pertaining to the sites book review data. 

The site is currently being hosted on Heroku and is accessible via this [link](https://dashboard.heroku.com/apps/cbenadebookreview).

Below are some brief explanations for each significant project file or folder contained in this repository: 
* [static](https://github.com/cbenade/CS50W-project1/tree/master/static): Folder containing stylesheet files for formatting the book review website
* [templates](https://github.com/cbenade/CS50W-project1/tree/master/templates): Folder containing html template files served to the user via the Flask application
    *[book_info.html](https://github.com/cbenade/CS50W-project1/blob/master/templates/book_info.html): Detailed book information page, users can view and post book-specific reviews at this location
    *[index.html](https://github.com/cbenade/CS50W-project1/blob/master/templates/index.html): Main search-entry page that the user is taken to upon successful login
    *[layout.html](https://github.com/cbenade/CS50W-project1/blob/master/templates/layout.html): Common HTML extracted out from each page's individual code
    *[login.html](https://github.com/cbenade/CS50W-project1/blob/master/templates/login.html): Login page where user is able to sign in   
    *[register.html](https://github.com/cbenade/CS50W-project1/blob/master/templates/register.html): Registration page where user is able to create their own individual account
    *[search.html](https://github.com/cbenade/CS50W-project1/blob/master/templates/search.html): Dynamic page that is generated for the user via database information matching the users previous search pattern 
* [application.py](https://github.com/cbenade/CS50W-project1/blob/master/application.py): Code containing instructions for the web application server. Instructs the server how to retrieve database information and generate dynamic web pages based on the users information and requests. Information served to the user is determined via URL requests and on this server an API tool has been included for other developers to request book-specific information.
* [books.csv](https://github.com/cbenade/CS50W-project1/blob/master/books.csv): Source file used to populate database book/author information. Only books contained in this file will appear on cbenadebookreview searches
* [helpers.py](https://github.com/cbenade/CS50W-project1/blob/master/helpers.py): File containing login decorator forcing users to login to the website before accessing specific book review information
* [import.py](https://github.com/cbenade/CS50W-project1/blob/master/import.py): File used to copy information from "books.csv" into the database hosted via the Heroku service
* [Procfile](https://github.com/cbenade/CS50W-project1/blob/master/Procfile): File used by Heroku to determine commands to be executed by the application on startup
* [requirements.txt](https://github.com/cbenade/CS50W-project1/blob/master/requirements.txt): File used by Heroku to determine which Python libraries need to be installed to successfully run and host the Python/Flask application
* [sql-table-queries-schema](https://github.com/cbenade/CS50W-project1/blob/master/sql-table-queries-schema): Plaintext file illustrating database schema and containing commands used in psql to create the database tables 
