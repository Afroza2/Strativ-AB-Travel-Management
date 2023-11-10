# Strativ-AB-Travel-Management

The weather in Dhaka is too hot to handle. Let's travel somewhere to cool off.

We have the latitude and longitude of all the districts of Bangladesh here:

https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json


Using the API from open-meteo.com, we can get the temperature forecasts of each districts for up to 7 days: https://open-meteo.com/en/docs


Now let's get to the interesting part.


1. Let's make an API for the coolest 10 districts based on the average temperature at 2pm for the next 7 days.
2. Now as we got the list, where do you want to travel and why?
3. Let's say your friend wants to travel as well and needs your help. Let's create an API where you take your friend's location, their destination, and the date of travel. Compare the temperature of those two locations at 2 PM on that day and return a response deciding if they should travel there or not. Hint: You might need to periodically fetch data and store it somewhere.
4. Constraint: API response should not exceed 0.5 seconds.
5. Train a simple model that forecasts the weather conditions in a given future date. To simplify things, restrict predictions to the Dhaka district. After training the model, the model should be query-able via a simple API. For example, your API should be able to predict the temperature at any future date (beyond the 7 days provided by OpenMeteo). *Note: If you feel that you do not have enough time and want to simplify further, provide a written solution plan for this section instead of a coded solution.*

# How to run the project?

1. run "pip install -r requirements.txt" on preferably a 3.10-based Python virtual environment.
2. Run Celery worker in one terminal - celery -A travelmanagement worker -l info
3. Run Celery beats in another terminal - celery -A travelmanagement beat -l info
4. Run Django in another terminal - python manage.py runserver
5. To run migrations, run "python manage.py makemigrations", "python manage.py migrate" and "python manage.py migrate django_celery_beat"
