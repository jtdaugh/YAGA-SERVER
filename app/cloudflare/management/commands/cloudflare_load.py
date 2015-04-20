from django.core.management.base import NoArgsCommand

from ...conf import settings
from ...utils import cloudflare_mask


class Command(
    NoArgsCommand
):
    help = 'Load Cloudflare proxies masks.'

    def handle_noargs(self, **options):
        if settings.CLOUDFLARE_BEHIND:
            cloudflare_mask.load_remote()
        else:
            self.stderr.write('Cloudflare is disabled')
