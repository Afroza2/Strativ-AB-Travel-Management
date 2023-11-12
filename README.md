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


   Github link - https://github.com/Afroza2/Strativ-AB-Travel-Management/tree/master

As I completed the previous step of this assignment, I completed the final task this time.

Steps that I followed along the way:

     1.I imagined this system as a predictor where based on my input, the API will return me the prediction as output. For this, I need to have-
a. An AI system that provides the model file
b. API view
c. Url for that view
      2. Point (a) is the most crucial part and took up most of the task. Here’s what I did-
 - First fetched the data using this url - https://open-meteo.com/en/docs , the code fetching and caching logic are provided in the website
While I checked the csv, I found out that data from June 2022 to before are missing, even though openmeteo has the data
- I searched and found the url for historical data, starting from 1940 till the day of starting this assignment. Every data point was present so there was no null value. Therefore, I did not have to preprocess any further. 
- First I started in a colab notebook, upon checking the python version (this is crucial, model and API need to be in same python version) I added the website code for data fetching, caching and creating dataframe
- I performed some EDA on the data to understand  and came to the conclusion that this is a time-series.
- Then I plotted the dataset, and to further confirm my hypothesis, I plotted the last 10 year’s data as a line plot. The time-series pattern is more discernible here.
- This observation narrowed down my model choice, as I either had to use ARIMA or Prophet. Due to time constraints I picked Prophet.
- The Prophet needs two columns as ‘ds’ and ‘y’. Basically my answer is the y. I renamed my dataframe and fit this into the model.
- It took me around 50 minutes to train this whole dataset, and I also had to switch from colab to jupyter for which the frequent commit was disrupted. Anyway, after the model training, I got the seasonality, trend and residuals, along with a number of insights.
- Finally, I wrote the logic to download the model as a file. The Prophet model can be downloaded only in json format, so that’s what I got.

       3. Now I imported the model inside my Django app and created a view for the API where the input (that is, the date) that I will provide will be passed inside the predict function of the Prophet model and I will receive the prediction.
       4. Then I added the url for the API - http://127.0.0.1:8000/api/predict-weather/ (POST), form_body date = “YYYY-MM-DD”
      5. The API response time was over a few seconds so I decided to optimize my model loading and querying logic. First, I tried sync_to_async decorator and keywords but soon I found out that the Prophet does not support asynchronous operation. 
      6. Celery shared_tasks logic suddenly came to mind. I wrote a function to load the model in the background, saved it in a redis cache and later loaded it from the cache only when I made a query. The response time drastically reduced to milliseconds.
 

