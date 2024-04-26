import os
import logging

from optparse import make_option
from ssl import AlertDescription
from lxml import etree

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError
from django.core.management import call_command

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
        already_loaded_batches = [b.name for b in Batch.objects.all()]
        batches = [
            d
            for d in os.listdir("data/batches")
            if os.path.isdir(os.path.join("data/batches", d))
            and d.startswith("batch_")
            and d not in already_loaded_batches
        ]

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
                call_command("load_batch", batch_path)
            else:
                LOGGER.error(f"batch {batch} not found")

        # since we skip index of titles above, we index here
        if len(batches_to_load) > 0:
          call_command("index_titles")
