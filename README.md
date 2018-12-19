# Django IMS Toolbox

Tools for Django to comply to different IMS standards.

Installation
------------

While this toolbox is under development it is recommended to add this toolbox as a submodule.
You can run the following commands in the root of your project:

```bash
git submodule add git@github.com:SURFpol/django_ims_toolbox.git ims
git submodule update
pip install ims/requirements.txt
./manage.py migrate
```

This should have setup the code and ran the migrations for the IMS toolbox.
Now it is possible to turn any Django view into an LTI component and work with IMSCC content through Django models.

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
The ```view``` needs to be the name of your view including any URL namespaces.
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
After you've added the LTI app to the LMS you should be able to "launch" it.

Upon launch the toolbox will create and/or login a user unless the ```privacy_level``` is set to ```anonymous```.
Information about the launch is available in the app view through ```request.session```.
Specifically the following data will be available:

*  ```roles``` specifies the roles of the launching user. This could be an empty string.
* ```api_domain``` specifies the domain under which the LMS API is available. This could be None.
* ```course_id``` the identifier of the course that acts as the context for the launch. This could be None.


Developing LTI views to launch
------------------------------

Any [view under a named URL pattern](https://docs.djangoproject.com/en/1.11/topics/http/urls/#examples)
can act as an LTI app. The toolbox will manage the "launch" for you.

During development you might want to "launch" the app without actually working with a LMS.
This is possible through the LTI debug URL. Visit this special view using:

```
http://localhost:8000/debug/your-lti-app-slug/
```

To control the launch you can set a number of query parameters. Currently the following parameters are available:

* ```client_key``` when set to a LTITenant.client_key it launches through that LTITenant.
  By default the last created LTITenant will be used for launch.
* ```user``` can be any string. It will become the username of the Django User instance. The default is "debug-user".
* Additionally the ```roles```, ```api_domain``` and ```course_id``` session data described above can be set
  by using the session keys as the parameters keys and giving any value to them.


Controlling LTI configurations
------------------------------

Just like HTML and different browsers there are different ways in which LMS's implement LTI.
These differences mostly manifest in LTI configurations.
Because the configuration should be depending on the LMS
and the LMS differs per organization the LTI configuration is controlled through the LTITenant model.

An LTITenant uses the dgconfig ConfigurationField to manage different configurations.
You can read more about that model field at the [dgconfig Github repo](https://github.com/fako/dgconfig).

To give one usage example here. Currently Canvas (a LMS) will display a link in its course navigation
if the ```tenant.lms``` equals ```Canvas``` and the tenant configuration
```tenant.config.canvas_course_navigation_visibility``` is set to a valid course navigation visibility value
(as defined by Canvas).


Work with IMS Archives
----------------------

There are two standards that define how content should be shared across parties.
The older *Content Package* and newer *Common Cartridge*.
Both standards are in use, but share a lot of functionality.
The IMSArchive model catches this shared logic.
It is the base class for the ContentPackage and CommonCartridge models,
which are proxy models that override some of the base methods.
