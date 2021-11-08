import os
import logging

from optparse import make_option
from ssl import AlertDescription
from lxml import etree

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.core.management import call_command

from django_q.tasks import async_task
from django_q.models import Task

from core.batch_loader import BatchLoader, BatchLoaderException
from core.management.commands import configure_logging
from core.models import Batch

configure_logging("load_batch_logging.config", "load_batch_%s.log" % os.getpid())

LOGGER = logging.getLogger(__name__)

def load_our_lccn(batch_xml):
    our_lccns = os.listdir("/open-oni/data/batches/marc")
    tree = etree.parse(batch_xml).getroot()
    lccns = [s.attrib["lccn"] for s in tree if s.attrib.get("lccn", False)]
    lccns = list(set(lccns))
    for lccn in lccns:
        if lccn in our_lccns:
            marc_xml = f"/open-oni/data/batches/marc/{lccn}/marc.xml"
            if os.path.isfile(marc_xml):
                LOGGER.info(f"loading title for {lccn}")
                call_command("load_titles", marc_xml, "--skip-index")
            else:
                LOGGER.error(f"we think we have marc data for {lccn} but we do not")


class Command(BaseCommand):
    help = """
    This command loads the metadata and pages associated with a batch into a
    database and search index. It may take up to several hours to complete,
    depending on the batch size and machine.
    """

    def handle(self, *args, **options):
        successful_tasks = Task.objects.filter(success=True)
        already_loaded_batches = [
            s.args[0].rstrip("/").split("/")[-1] for s in successful_tasks
        ]
        batches_env = os.getenv("BATCHES_ENV", "dev")
        batches_file = f"data/batches/batches-{batches_env}.txt"
        if os.path.isfile(batches_file):
            with open(batches_file, "r") as f:
                batches = [line.strip() for line in f.readlines() if line.strip()]
        else:
            raise ValueError(f"file {batches_file} does not exist")

        batches_to_load = [
            batch for batch in batches if batch not in already_loaded_batches
        ]
        LOGGER.info(f"found {len(batches_to_load)} batches to load")

        for batch in batches_to_load:
            batch_path = f"/open-oni/data/batches/{batch}"
            batch_xml = f"{batch_path}/data/BATCH.xml"

            # If we have custom marc.xml for a given lccn, we load it before calling the load_batch command
            if os.path.isfile(batch_xml):
                load_our_lccn(batch_xml)
            if os.path.isfile(batch_xml.lower()):
                load_our_lccn(batch_xml.lower())

            if os.path.isdir(batch_path):
                LOGGER.info(f"loading batch {batch}")
                async_task(
                    "core.management.commands.load_batch_async.load_batch", batch_path
                )
            else:
                LOGGER.error(f"batch {batch} not found")

        # since we skip index of titles above, we index here
        call_command("index_titles")
