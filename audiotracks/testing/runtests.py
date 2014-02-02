import sys
import os

from django.conf import settings

HERE_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_ROOT = os.path.join(HERE_DIR, "site_media")


def main():
    settings.configure(
        HERE_DIR=os.path.dirname(os.path.abspath(__file__)),
        MEDIA_ROOT=os.path.join(HERE_DIR, "site_media"),
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': 'test.db',
            }
        },
        ROOT_URLCONF='audiotracks.testing.urls',
        SITE_ID=1,
        INSTALLED_APPS=(
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.sites",
            "audiotracks",
        ),
        AUDIOTRACKS_PER_PAGE=3,
        SECRET_KEY = 'test secret key'
    )
    from django.test.utils import get_runner
    runner = get_runner(settings)(verbosity=1, interactive=True)
    failures = runner.run_tests(['audiotracks'])
    sys.exit(failures)

if __name__ == "__main__":
    main()
