===============
django-honeypot
===============

.. image:: https://github.com/jamesturk/django-honeypot/actions/workflows/test.yml/badge.svg

.. image:: https://img.shields.io/pypi/v/django-honeypot.svg
    :target: https://pypi.python.org/pypi/django-honeypot

Django application that provides utilities for preventing automated form spam.

Provides template tags, view decorators, and middleware to add and verify honeypot fields to forms.

Written by James Turk with contributions by Flavio Curella and Daniel Greenfeld.

Source: https://github.com/jamesturk/django-honeypot/

Requirements
============

* python >= 3.8
* django >= 3.2

Usage
=====

settings.py
-----------

Be sure to add ``honeypot`` to ``INSTALLED_APPS`` in settings.py.

You will almost always need to define ``HONEYPOT_FIELD_NAME`` which is the name to use for the honeypot field.  Some sophisticated bots will attempt to avoid fields named honeypot, so it may be wise to name the field something slightly more realistic such as "phonenumber" or "body2".

``HONEYPOT_VALUE`` is an option that you can specify to populate the honeypot field, by default the honeypot field will be empty and any text entered into it will result in a failed POST.  ``HONEYPOT_VALUE`` can be a string or a callable that takes no arguments.

``HONEYPOT_VERIFIER`` is an advanced option that you can specify to validate the honeypot.  The default verifier ensures that the contents of the honeypot field matches ``HONEYPOT_VALUE``.  Using a combination of a callable for ``HONEYPOT_VALUE`` and ``HONEYPOT_VERIFIER`` it is possible to implement a more advanced technique such as using timestamps.

``HONEYPOT_RESPONDER`` can be used to replace the default response in case of an invalid honeypot.

Adding honeypot fields to specific forms and views
--------------------------------------------------

It is possible to add honeypot fields to specific forms and ensure that specific views check for a valid honeypotin ``request.POST``.  This can be accomplished by using the ``render_honeypot_field`` template tag:

At the top of a template file include the line::

    {% load honeypot %}

And then within any form including the tag::

    {% render_honeypot_field "field_name" %}

will render a honeypot field named "field_name" that is hidden by default.  The name of the honeypot field will default to ``HONEYPOT_FIELD_NAME`` if one is not provided.

To ensure that the honeypot field is both present and correct you will need to use ``check_honeypot`` decorator from ``honeypot.decorators``:

.. code:: python

    from honeypot.decorators import check_honeypot

    @check_honeypot(field_name='hp_field_name')
    def post_comment(request):
        ...

    @check_honeypot
    def other_post_view(request):
        ...

This decorator will ensure that a field exists in ``request.POST`` that is named 'field_name'.  ``@check_honeypot`` without arguments will use the default ``HONEYPOT_FIELD_NAME``.

Adding honeypot fields to class-based-views
-------------------------------------------

The same as above for `Adding honeypot fields to specific forms and views`_ but add the decorator to the post method making use of django's `method_decorator <https://docs.djangoproject.com/en/3.2/topics/class-based-views/intro/#decorating-the-class>`_.


.. code:: python

    from django.utils.decorators import method_decorator
    from honeypot.decorators import check_honeypot

    @method_decorator(check_honeypot, name='post')
    class MyView(FormView):
        ...

Adding honeypot fields site-wide
--------------------------------

Sometimes it is desirable to add honeypots to all forms site-wide.  This is particularly useful when dealing with apps that render their own forms.  For this purpose three middlewares are provided, similar in functionality to django's own CSRF middleware.

All of these middleware live in ``honeypot.middleware``.

``HoneypotResponseMiddleware`` analyzes the output of all responses and rewrites any forms that use ``method="POST"`` to contain a honeypot field, just as if they had started with ``{% render_honeypot_field %}``.  Borrowing heavily from ``django.contrib.csrf.middleware.CsrfResponseMiddleware`` this middleware only rewrites responses with Content-Type text/html or application/xhtml+xml.

``HoneypotViewMiddleware`` ensures that for all incoming POST requests to views ``request.POST`` contains a valid honeypot field as defined by the ``HONEYPOT_FIELD_NAME``, ``HONEYPOT_VALUE``, and ``HONEYPOT_VERIFIER`` settings.  The result is the same as if every view in your project were decorated with ``@check_honeypot``.

``HoneypotMiddleware`` is a combined middleware that applies both ``HoneypotResponseMiddleware`` and ``HoneypotViewMiddleware``, this is the easiest way to get honeypot fields site-wide and can be used in many if not most cases. The middleware needs to be listed after ``CommonMiddleware`` because the middleware changes the response. If you list it before  ``CommonMiddleware`` then the ``Content-Length`` header won't reflect the changes.

Customizing honeypot display
----------------------------

There are two templates used by django-honeypot that can be used to control various aspects of how the honeypot functionality is presented to the user.

``honeypot/honeypot_field.html`` is used to render the honeypot field.  It is given two context variables ``fieldname`` and ``value``, corresponding to ``HONEYPOT_FIELD_NAME`` and ``HONEYPOT_VALUE`` or any overrides in effect (such as a custom field name passed to the template tag).

``honeypot/honeypot_error.html`` is the error page rendered when a bad request is intercepted.  It is given the context variable ``fieldname`` representing the name of the honeypot field.

To completely change the error page or what happens when a bad request is intercepted set ``HONEYPOT_RESPONDER`` to a function accepting ``request`` and ``context`` kwargs and returning a ``HttpResponse``.

.. code:: python

    # settings.py
    HONEYPOT_FIELD_NAME = 'text-message'
    HONEYPOT_RESPONDER = 'your_app_name.views.honeypot_view_function'


.. code:: python

    # your_app_name/views.py
    def honeypot_view_function(request, fieldname):
        fieldname = fieldname
        data = {
            'ip_address': request.META['REMOTE_ADDR'],
            'url_path': request.path,
        }
        print(f'django honeypot detect spam from ip: {data['ip_address']} in uri: {data['url_path']} and field: {fieldname}')

        return render(request, "honeypot/honeypot_error.html", status=200)

    # output:
    # django honeypot detect spam from ip: 192.168.48.208 in uri: /contact/contact/ and field: {'fieldname': 'text-message'}
    # plus http response with status code 200 and template 'honeypot/honeypot_error.html'
