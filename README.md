# photo-store
A storefront API for ordering prints of photographs.

Written in Python using the Django framework.

## Set up

This project assumes you have Python 3.5 or later installed on your machine.
It uses pipenv to manage dependencies. Follow the instructions below to set up pipenv.

- install pipenv
```
python3 -m pip install pipenv
```
- install project dependencies
```
cd photo_store
python3 -m pip pipenv install
```

## Run
The dependencies have been installed. Run the following commands to run the application.
```
pipenv shell
cd photo_store
python manage.py runserver
```

## Endpoints
```
http://127.0.0.1:8000/photo-store/photos/ - GET returns all photos
http://127.0.0.1:8000/photo-store/order/ - POST with correct form data places an order
```

## Credits
The images used in this project were obtained from here: http://www.vision.caltech.edu/Image_Datasets/Caltech101/
