import django.dispatch

direct_upload_success = django.dispatch.Signal(providing_args=["name", "request"])
