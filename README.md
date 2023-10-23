# Strativ-AB-Travel-Management

The weather in Dhaka is too hot to handle. Let's travel somewhere to cool off.

We have the latitude and longitude of all the districts of Bangladesh here:

https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json


Using the API from open-meteo.com, we can get the temperature forecasts of each districts for up to 7 days: https://open-meteo.com/en/docs


Now let's get to the interesting part.


Let's make an API for the coolest 10 districts based on the average temperature at 2pm for the next 7 days.
Now as we got the list, where do you want to travel and why?
Let's say your friend wants to travel as well and needs your help. Let's create an API where you take your friend's location, their destination, and the date of travel. Compare the temperature of those two locations at 2 PM on that day and return a response deciding if they should travel there or not. Hint: You might need to periodically fetch data and store it somewhere.
Constraint: API response should not exceed 0.5 seconds

