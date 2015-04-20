from __future__ import absolute_import, division, unicode_literals
from future.builtins import (  # noqa
    ascii, bytes, chr, dict, filter, hex, input, int, list, map, next, object,
    oct, open, pow, range, round, str, super, zip
)

from django.db import models
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _

from app.model_fields import UUIDField


@python_2_unicode_compatible
class Mask(
    models.Model
):
    id = UUIDField(
        auto=True,
        primary_key=True,
        version=4
    )

    value = models.CharField(
        verbose_name=_('Mask'),
        max_length=255,
        unique=True
    )

    created_at = models.DateTimeField(
        verbose_name=_('Created At'),
        auto_now_add=True
    )

    class Meta:
        verbose_name = _('Mask')
        verbose_name_plural = _('Masks')

    def __str__(self):
        return self.value
