import glob
import logging
import os
import requests
import time
from urllib import parse

from django.core.management.base import BaseCommand
from django.conf import settings
from core.management.commands import configure_logging

configure_logging('setup_index_logging.config', 'setup_index.log')


_logger = logging.getLogger(__name__)
fixture_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../fixtures'))
if settings.SOLR_CLOUD:
    core_url = settings.SOLR_BASE_URL + '/api/collections/openoni?action=STATUS&indexInfo=true'
    schema_url = settings.SOLR_BASE_URL + '/api/collections/openoni/schema'
else:
    core_url = settings.SOLR_BASE_URL + '/api/cores/openoni?action=STATUS&indexInfo=true'
    schema_url = settings.SOLR_BASE_URL + '/api/cores/openoni/schema'


class Command(BaseCommand):
    help = 'Set up all Solr index configuration necessary for Open ONI'

    def handle(self, **options):
        _logger.info('Creating Collection openoni')

        r = requests.get(settings.SOLR_BASE_URL + '/solr/admin/collections', params={"action":"LIST"})
        if r.status_code == 200:
            if 'openoni' in r.json().get('collections', []):
                _logger.info('Collection exists not modifying')
                pass

        # create the collection
        params = {
           "action": "CREATE",
           "name": "openoni",
           "numShards": 1,
           "replicationFactor": 1,
           "maxShardsPerNode": 1,
           "collection.configName": "_default"
        }
        r = requests.get(settings.SOLR_BASE_URL + '/solr/admin/collections', params=params)
