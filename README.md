# Auctions

CS50w Auctions Project allong with a full featured API.

![Listings page](/screenshots/main.jpg)

![REST API](/screenshots/api.jpg)

## About

The course third project consists of a eBay-like e-commerce auction site, build with **Django**, that allow users to post auction listings, place bids on listings, comment on those listings, and add listings to a “watchlist”.

As custom features (in addition to those required by the course) I implemented:

-   **Time limited listings**. The users are required inform in advance (during the creation of a auction) a duration for listing, wich can selected between five options: one day, three days, one week, two weeks or one month;
-   A custom styling with the **Bootstrap framework**, wich includes a navigation bar with a dropdown for navigation categories and a inline count of items in the watchlist;
-   A **search bar**, where the users can query for listings titles;
-   And a **flash messages** system with the Django messages functionallity, where the users are informed about their operations in the app, like posting bids and closing actions;
-   An API for with the Django REST Framework, where a client can retrieve the data from the database in JSON format;
-   A task queue system (with the Celery framework and Redis as broker and backend), that is used to store and execute scheduled and periodic tasks in the backgroud;

Also, during this project I could learn about

-   The **Object Relational Mapping** (ORM) system that Django provides as a **database-abstraction API** to develop data driven web applications;
-   Creation of Django Models to represent the data that the users can interact with;
-   **CRUD** operations in Django, including the use of the **QuerySet** functionallity;
-   Django Forms functionallity, including model based forms, rendering of form fields on the web pages and users input processing from Django Forms;
-   Security in web forms, including Cross-site Request Forgery (CSRF) attacks and the csrf tokens that Django provides to defend against them;
-   User authentication;
-   Context managment in dinamically generated web pages;
-   Unit testing with Python unittest and the Django Tests extension for it;
-   Docker consteiners and the importance of standardization of environments during web development for conpatibility assurence;
-   Different database management systems and paradigms, like Redis, as a NoSQL database and PostgreSQL as relational database;
-   RESTfull APIs development.

## Project Snapshot

<h3 align="center">Login page</h3>

![Login page](/screenshots/login.jpg)

<h3 align="center">Registration page</h3>

![Registration page](/screenshots/register.jpg)

<h3 align="center">Listing page</h3>

![Listing page](/screenshots/listing.jpg)

<h3 align="center">Search</h3>

![Serch](/screenshots/search.jpg)

<h3 align="center">Categories menu</h3>

![Categories menu](/screenshots/categories.jpg)

<h3 align="center">Create Listing page</h3>

![Create Listing page](/screenshots/create.jpg)

<h3 align="center">Flash messages</h3>

![Flash messages](/screenshots/messages.jpg)

<h3 align="center">Watchlist</h3>

![Watchlist](/screenshots/watchlist.jpg)
