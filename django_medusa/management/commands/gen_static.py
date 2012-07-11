import os


from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.contrib.sites.models import Site

from optparse import make_option

from django_medusa.renderers import StaticSiteRenderer
from django_medusa.utils import get_static_renderers

from utils import make_tls_property


SITE_ID = settings.__dict__['_wrapped'].__class__.SITE_ID = make_tls_property(settings.SITE_ID)
MEDUSA_DEPLOY_DIR = settings.__dict__['_wrapped'].__class__.MEDUSA_DEPLOY_DIR = make_tls_property(settings.MEDUSA_DEPLOY_DIR)


class Command(BaseCommand):
    help = 'Looks for \'renderers.py\' in each INSTALLED_APP, which defines '\
           'a class for processing one or more URL paths into static files.'
    args = '<domain_name domain_name ...>'

    option_list = BaseCommand.option_list + (
    make_option('-l', '--list',
        action='store_true',
        dest='list_sites',
        default=False,
        help='List all available sites with domain names.'),
    )

    can_import_settings = True

    def handle(self, *args, **options):

        if options.get('list_sites'):
            print '\n'.join([site.domain for site in Site.objects.all()])

        for domain_name in args:
            try:
                site = Site.objects.get(domain=domain_name)
            except Site.DoesNotExist:
                raise CommandError("Site %s does not exist" % domain_name)

            SITE_ID.value = site.id
            MEDUSA_DEPLOY_DIR.value = os.path.join(
                settings.PROJECT_ROOT, 'static_sites', site.domain
            )

            StaticSiteRenderer.initialize_output()

            for Renderer in get_static_renderers():
                r = Renderer()
                r.generate()

            StaticSiteRenderer.finalize_output()