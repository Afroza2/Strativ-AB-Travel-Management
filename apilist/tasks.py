from celery import shared_task


@shared_task
def fetch_hourly_data_function(s):
    return s

@shared_task
def add(x, y):
    
    return x + y
