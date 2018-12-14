# Django IMS Toolbox

Tools for Django to comply to different IMS standards.

Installation
------------

While this toolbox is under development it is recommended to add this toolbox as a submodule.
You can run the following commands in the root of your project:

```bash
git submodule add git@github.com:SURFpol/django_ims_toolbox.git ims
git submodule update
./manage.py migrate
```

This should have setup the code and ran the migrations for the IMS toolbox.
Now it is possible to turn any view into an LTI component and work with IMSCC content

Work with LTI
-------------

In order to work with the LTI launch system from the toolbox some additional steps are required.
You'll have to add the LTI URL patterns to your projects urls.py.
The debug URL patterns are optional, but they are recommended during development.

```python
from django.conf.urls import url
from django.conf import settings
from ims import views as ims_views


urlpatterns = []

if settings.DEBUG:
    urlpatterns += [
        url(r'^debug/(?P<slug>[A-Za-z0-9\-]+)/?$', ims_views.lti_debug_launch)
    ]

urlpatterns += [
    url(
        r'^(?P<app_slug>[A-Za-z0-9\-]+)/config/(?P<tenant_slug>[A-Za-z0-9\-]+)\.xml$',
        ims_views.lti_config,
        name='lti-config'
    ),
    url(r'^(?P<slug>[A-Za-z0-9\-]+)/?$', ims_views.lti_launch)
]
```

We're going to assume that you have a
[named Django view](https://docs.djangoproject.com/en/1.11/topics/http/urls/#examples)
in your project that you're going to launch as an LTI app.

To setup the LTI go to the admin and create a LTIApp.
The ```slug``` will be the URL under which your LTI app will be visible for users.
For the most part the slug will be opaque, but it's wise to choose a name that makes sense to you.
The ```view``` needs to be the name of your view including any namespaces.
```title``` and ```description``` will be visible to the user and should explain your app.
The ```privacy level``` follows the IMS LTI specification
and indicates what level of user information gets passed on to your app.
A value of ```public``` means that both email address and name will be passed on.

After creating your LTIApp in the admin you'll have to add at least one LTITenant.
The LTITenant model holds all information about the organization that want to use the LTIApp inside its LMS.
To add a LTITenant you'll have to specify which ```app``` the tenant is for
as well as the ```organization``` name and the ```LMS``` the tenant will use.
Lastly ```slug``` can be any valid slug and again this value will be mostly opaque to end users.

Once you save your LTITenant it generates a config.xml link
and the consumer information that you need to add a LTI app to a LMS.
After you've added the LTI app to the LMS you should be able to launch it.


Developing LTI views to launch
------------------------------


Work with IMS Archives
----------------------
