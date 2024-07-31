from django.http import HttpResponse
from functools import wraps
from datetime import datetime

def check_date(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        threshold_date = datetime(2024, 8, 2)
        current_date = datetime.now()

        if current_date >= threshold_date:
            return HttpResponse("Please contact the developer", content_type="text/plain")
        return view_func(request, *args, **kwargs)

    return _wrapped_view
