# Ear ninja

## Description

Ear ninja is an [ear training](https://en.wikipedia.org/wiki/Ear_training) web app written in Python and Django. Currently, there is one exercise working: [interval recognition](https://en.wikipedia.org/wiki/Interval_recognition).

The app is deployed [here](https://tgrykias.eu.pythonanywhere.com/). At present, it requires creating an account to use it.

## How to run

Here are instructions that should be sufficient to run the app locally or deploy it on [PythonAnywhere](https://www.pythonanywhere.com/).

To deploy the app follow the following steps:

1. Clone the repository (instructions assume that the app will be in directory: `~/django_projects/ear-ninja/`) 

```
cd ~/django_projects/
git clone git@github.com:tgrykias58/ear-ninja.git
```

2. If virtualenvwrapper is not installed, follow [these](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/development_environment#using_django_inside_a_python_virtual_environment) instructions.

3. Create and activate Python virtual environment:
```
mkvirtualenv --python=python3.10 ear-ninja
workon ear-ninja
```

4. Install requirements in this virtual environment:

```
cd ~/django_projects/ear-ninja/
pip3 install -r requirements.txt
```

5. Create .env file:
```
touch ~/django_projects/ear-ninja/earninja/.env
```

6. Open this file in a text editor and set the following variables: `DJANGO_DEBUG`, `SECRET_KEY`, `SESSION_COOKIE_SECURE`, `CSRF_COOKIE_SECURE`, `SECURE_SSL_REDIRECT`, `SECURE_HSTS_SECONDS`, `SECURE_HSTS_PRELOAD`, `SECURE_HSTS_INCLUDE_SUBDOMAINS`. Their values are different for development and production environments. They are described in detail in [the official Django documentation](https://docs.djangoproject.com/en/4.2/ref/settings/).

7. Install [fulidsynth](https://www.fluidsynth.org/). It's used by the app for generating `.wav` files from `midi` files. If you have `sudo` access then installing fluidsynth can be done by simply:  
```
sudo apt-get update
sudo apt-get install fluidsynth
```
If you don't have `sudo` privileges (e.g. [on PythonAnywhere](https://help.pythonanywhere.com/pages/InstallingNewModules/#4-installing-non-python-packages)) then follow instructions from [this section](#installing-fluidsynth-from-source).

8. Download a [soundfont](https://github.com/FluidSynth/fluidsynth/wiki/SoundFont) for fluidsynth. [This one](https://www.schristiancollins.com/generaluser.php) is recommended. Move it to the path `/home/yourusername/.fluidsynth/soundfont.sf2` (replace "yourusername" by your username).

9. If [fulidsynth](https://www.fluidsynth.org/) has been installed with `apt-get`, then set related variables in `.env` file as follows (again, remember to replace "yourusername" by your username):

```
FLUIDSYNTH_PATH='fluidsynth'
SOUNDFONT_PATH='/home/yourusername/.fluidsynth/soundfont.sf2'
```

10. Run:
```
cd ~/django_projects/ear-ninja/earninja/
python manage.py collectstatic --no-input
python manage.py makemigrations
python manage.py migrate
```

11. At this point, you should be able to run tests:
```
cd ~/django_projects/ear-ninja/earninja/
python manage.py test
```

12. The app should be ready for local development. Run the following to start the app (doesn't work on PythonAnywhere):

```
cd ~/django_projects/ear-ninja/earninja/
python manage.py runserver
```

12. If you're deploying the app on PythonAnywhere, follow [these instructions](https://developer.mozilla.org/en-US/docs/Learn/Server-side/Django/Deployment#setup_the_web_app) (remember to change the name of the app to "ear-ninja" etc.). The relevant part here is "Setup the web app" subsection of "Example: Hosting on PythonAnywhere".

13. If you're on PythonAnywhere and using `DJANGO_DEBUG=False` then create a [mapping for media files in static files section](https://stackoverflow.com/questions/42505292/media-files-not-showing-on-debug-false/42505333). Go to `Web app` tab on PythonAnywhere, then to the `Static files` section and set this mapping (again, replace "yourusername" by your username): 
```
URL: /media/
Directory: /home/yourusername/django_projects/ear-ninja/earninja/media/ 
```

## Installing fluidsynth from source

It might happen that you're deploying the Ear ninja app in an environment where you don't have `sudo` privileges and cannot use `apt-get` to install `fluidsynth`. For example, this is an issue [on PythonAnywhere](https://help.pythonanywhere.com/pages/CompilingCPrograms). 

The app can still be deployed in this case, but it requires installing `fluidsynth` from source as described [here](https://github.com/FluidSynth/fluidsynth/wiki/BuildingWithCMake).

To do this follow these steps:

1. Download `Source code.tar.gz` from [this link](https://github.com/FluidSynth/fluidsynth/releases) (tested on version `2.3.4`). Move it to path: `~/django_projects/fluidsynth-2.3.4.tar.gz`.

2. Run (replace "yourusername" by your user name):
```
cd ~/django_projects/
tar -xvzf fluidsynth-2.3.4.tar.gz
cd fluidsynth-2.3.4/
mkdir build
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=/home/yourusername/fluidsynth
make install
```
3. Open `ear-ninja/earninja/.env` file in text editor and set following variables (remember to replace "yourusername" by your username):

```
FLUIDSYNTH_PATH='/home/yourusername/fluidsynth/bin/fluidsynth'
LD_LIBRARY_PATH=/home/yourusername/fluidsynth/lib:$LD_LIBRARY_PATH
```

## Speeding up the app

When new question is generated and a musical interval is encountered for first time, an `.mp3` file will be generated on the server, for this interval. On subsequent requests for this interval,`.mp3` file will be reused. 

Right after deployment, all intervals will be encountered for the first time, so it might lead to noticeable delays between clicking "Next" button and new question being presented to the user. There are several ways to mitigate this issue:


1. Use [Celery](https://docs.celeryq.dev/en/v5.3.6/getting-started/introduction.html) to generate audio files asynchronously. To use this option, set `USE_CELERY=True` in `earninja/earninja/settings.py` and configure Celery with Redis, perhaps following [this tutorial](https://realpython.com/asynchronous-tasks-with-django-and-celery/). 

Celery is [not supported on PythonAnywhere](https://www.pythonanywhere.com/forums/topic/1215/)

2. Pre-generate audio files for (most) intervals by running this script:
```
cd ~/django_projects/ear-ninja/earninja/
python manage.py runscript prepare_intervals --script-args 1 6
```
Arguments 1 6 mean here that intervals will be generated for octaves from range 1, 6 (1 and 6 included).

A downside of this approach is that if you're using a free account on PythonAnywhere, then you might exceed daily CPU allowance of 100 seconds.

3. Just wait until the app "warms up" with usage and a never requested interval becomes a rare thing.

## Known issues

If [autoplay](https://developer.mozilla.org/en-US/docs/Web/Media/Autoplay_guide) is blocked on Firefox browser, then question audio doesn't play after clicking "Next" button (you have to click "Repeat" for each question). If you encounter this issue, you can solve it by [enabling autoplay](https://support.mozilla.org/en-US/kb/block-autoplay) for Ear Ninja.