import os
import logging

from optparse import make_option
from ssl import AlertDescription

from django.core.management.base import BaseCommand
from django.core.management.base import CommandError

from django_q.tasks import async_task
from django_q.models import Task

from core.batch_loader import BatchLoader, BatchLoaderException
from core.management.commands import configure_logging
from core.models import Batch
    
configure_logging('load_batch_logging.config', 
                  'load_batch_%s.log' % os.getpid())

LOGGER = logging.getLogger(__name__)

class Command(BaseCommand):
    help = """
    Looks at failed tasks, reruns the job, and removes the failed item from
    the database
    """

    def handle(self, *args, **options):
        failed_tasks = Task.objects.filter(success=False)
        for task in failed_tasks:
            print(f"requeuing {task.args[0]}")
            async_task("core.management.commands.load_batch_async.load_batch", task.args[0])
            print(f"removing failed task from failed queue")
            task.delete()