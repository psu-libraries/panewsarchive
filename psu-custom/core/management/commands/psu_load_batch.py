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
        batches_env = os.getenv('BATCHES_ENV', 'dev')
        batches_file = f"data/batches/batches-{batches_env}.txt"
        if os.path.isfile(batches_file):
            with open(batches_file, 'r') as f:
                batches = [line.strip() for line in f.readlines() if line.strip()]
        else:
            raise ValueError(f"file {batches_file} does not exist")

        batches_to_load = [batch for batch in batches if batch not in already_loaded_batches]
        LOGGER.info(f"found {len(batches_to_load)} batches to load")

        for batch in batches_to_load:
            batch_path = f"/open-oni/data/batches/{batch}"
            if os.path.isdir(batch_path):
                LOGGER.info(f"loading batch {batch}")
                async_task("core.management.commands.load_batch_async.load_batch", batch_path)
            else:
                LOGGER.info(f"batch {batch} not found")