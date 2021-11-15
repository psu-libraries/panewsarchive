import os
import logging

from lxml import etree

from optparse import make_option
import urllib

from django.conf import settings
from django.db import connection
from django.core.management.base import BaseCommand, CommandError
from django.core.management import call_command

from core.batch_loader import BatchLoader, BatchLoaderException
from core.management.commands import configure_logging
from core.models import Batch
from core import solr_index

configure_logging('purge_batches_logging.config',
                  'purge_batch_%s.log' % os.getpid())

log = logging.getLogger(__name__)
# some xml namespaces used in batch metadata
ns = {
    'ndnp'  : 'http://www.loc.gov/ndnp',
    'mods'  : 'http://www.loc.gov/mods/v3',
    'mets'  : 'http://www.loc.gov/METS/',
    'np'    : 'urn:library-of-congress:ndnp:mets:newspaper',
    'xlink' : 'http://www.w3.org/1999/xlink',
    'mix'   : 'http://www.loc.gov/mix/',
    'xhtml' : 'http://www.w3.org/1999/xhtml'
}

def _find_batch_file(batch):
    """
    TODO: Who can we toss the requirement at to make this
    available in a canonical location?
    """
    # look for batch_1.xml, BATCH_1.xml, etc
    for alias in ["batch_1.xml", "BATCH_1.xml", "batchfile_1.xml", "batch_2.xml", "BATCH_2.xml", "batch.xml"]:
        # TODO: might we want 'batch.xml' first? Leaving last for now to
        # minimize impact.
        url = urllib.parse.urljoin(batch.storage_url, alias)
        try:
            u = urllib.request.urlopen(url)
            validated_batch_file = alias
            break
        except urllib.error.HTTPError as e:
            continue
        except urllib.error.URLError as e:
            continue

    return validated_batch_file

def batch_pages_count(batch):
    pages = 0
    batch_file = _find_batch_file(batch)
    batch_url = os.path.join(batch.storage_url, batch_file)
    doc = etree.parse(batch_url)
    for e in doc.xpath('ndnp:issue', namespaces=ns):
        mets_url = urllib.parse.urljoin(batch.storage_url, e.text)
        issues = etree.parse(mets_url)
        div = issues.xpath('.//mets:div[@TYPE="np:issue"]', namespaces=ns)[0]
        for page_div in div.xpath('.//mets:div[@TYPE="np:page"]',
                                  namespaces=ns):
            pages+=1

    return pages

class Command(BaseCommand):
    help = "Count pages of batch on disk, compares it to batches counted during load"


    def add_arguments(self, parser):
        # Options
        parser.add_argument('--batch',
                            default=None, dest='batch',
                            help='Batch name to verify')

        parser.add_argument('--purge', action='store_true',
                            default=False, dest='purge',
                            help='Purge out of sync batches')

    def handle(self, *args, **options):
        if options['batch']:
            batches = Batch.objects.filter(name=options['batch'])
        else:
            batches = Batch.objects.all()

        if len(batches) == 0:
            raise ValueError("batch not found")

        for batch in batches:
            log.info(f"Processing {batch.name}")
            db_count = batch.page_count

            disk_count = batch_pages_count(batch)
            if db_count == disk_count:
                log.info(f"{batch.name} db matches disk")
            else:
                if options['purge']:
                    call_command("purge_batch", batch.name)
                log.error(f"{batch.name} has {db_count} pages loaded, but {disk_count} on disk")