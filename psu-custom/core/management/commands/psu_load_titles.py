import logging

import os
from optparse import make_option

from django.core.management.base import BaseCommand
from django.utils import timezone

from django.core.management import call_command

from core import title_loader
from core import solr_index
from core.models import Title
from core.management.commands import configure_logging
import os

configure_logging('load_titles_logging.config', 'load_titles.log')
_logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = """
    Loads titles into Open ONI from a single file or a path containing multiple
    files.  All files must contain valid MARC XML.
    """
    def handle(self, *args, **options):
        #TODO add this as an argument with default
        path = "/open-oni/data/batches/marc"
        for root, directories, file in os.walk(path):
            for file in file:
                if(file == "marc.xml"):
                    print(os.path.join(root,file))
                    call_command("load_titles", os.path.join(root,file))