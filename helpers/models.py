
from django.db import models
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _ 

from core.helpers import generate_unique_slug

class BaseModel(models.Model):
    created_at = models.DateTimeField(_('Created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('Updated at'), auto_now_add=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if hasattr(self, 'slug') and hasattr(self, 'title'):
            if self.slug:
                if slugify(self.title) != self.slug:
                    self.slug = generate_unique_slug(self.__class__, self.title)
            else:
                self.slug = generate_unique_slug(self.__class__, self.title)

        if hasattr(self, 'slug') and hasattr(self, 'name'):
            if self.slug:
                if slugify(self.name) != self.slug:
                    self.slug = generate_unique_slug(self.__class__, self.name)
            else:
                self.slug = generate_unique_slug(self.__class__, self.name)

        super().save(*args, **kwargs)



