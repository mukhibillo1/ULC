
from django.template import defaultfilters 
from unidecode import unidecode 

def generate_unique_slug(klass, field):
    origin_slug = defaultfilters.slugify(unidecode(field))
    unique_slug = origin_slug
    numb = 1
    while klass.objects.filter(slug=unique_slug).exists():
        unique_slug = '%s-%d' % (origin_slug, numb)
        numb += 1 
    return unique_slug


