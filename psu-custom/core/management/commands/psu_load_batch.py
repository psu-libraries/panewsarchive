import os
import logging

from optparse import make_option
from ssl import AlertDescription

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from django_q.tasks import async_task

from core.batch_loader import BatchLoader, BatchLoaderException
from core.management.commands import configure_logging
from core.models import Batch
    
configure_logging('load_batch_logging.config', 
                  'load_batch_%s.log' % os.getpid())

LOGGER = logging.getLogger(__name__)


def load_batch(batch_path):
    loader = BatchLoader(process_coordinates=True, process_ocr=True)
    try:
        batch = loader.load_batch(batch_path)
    except BatchLoaderException as e:
        LOGGER.exception(e)
        raise CommandError("Batch load failed. See logs/load_batch_#.log")


class Command(BaseCommand):
    help = """
    This command loads the metadata and pages associated with a batch into a
    database and search index. It may take up to several hours to complete,
    depending on the batch size and machine.
    """

    def handle(self, *args, **options):
        already_loaded_batches = [ b.name for b in Batch.objects.all() ]
        batches  = [d for d in os.listdir('data/batches') if d.startswith("batch_") and d not in already_loaded_batches]

        for batch in batches:
            LOGGER.info(f"loading batch {batch}")
            batch_path = "/open-oni/data/batches/" + batch
            async_task("core.management.commands.load_batch_async.load_batch", batch_path)