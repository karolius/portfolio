import os
import shutil
import random
from PIL import Image
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.utils.text import slugify
from django.core.files import File


def download_media_location(instance, filename):
    return "%s/%s" % (instance.slug, filename)


class Product(models.Model):
    title = models.CharField(max_length=120)
    description = models.TextField()
    slug = models.SlugField(unique=True, blank=True)
    price = models.DecimalField(max_digits=25, decimal_places=2)
    sale_price = models.DecimalField(max_digits=25, decimal_places=2,
                                     null=True, blank=True)
    sale_active = models.BooleanField(default=False)
    media = models.ImageField(upload_to=download_media_location,
                              null=True, blank=True,
                              storage=FileSystemStorage(location=settings.PROTECTED_ROOT))

    def __str__(self):
        return self.title


def create_slug(instance, new_slug=None):
    if new_slug:
        slug = new_slug
    else:
        slug = slugify(instance.title)

    slug_exists = Product.objects.filter(slug=slug).exists()
    if slug_exists:
        new_slug = "%s-%s" % (slug, instance.id)
        return create_slug(instance, new_slug=new_slug)
    return slug


def product_pre_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = create_slug(instance)


pre_save.connect(product_pre_save_receiver, sender=Product)


THUMB_CHOICES = (("hd", "HD"),
                 ("sd", "SD"),
                 ("micro", "Micro"),)

THUMB_SIZE = ((500, 500),
              (350, 350),
              (150, 150))


def thumbnail_location(instance, filename):
    return "%s/%s" % (instance.product.slug, filename)


class Thumbnail(models.Model):
    product = models.ForeignKey(Product)
    type = models.CharField(max_length=12, choices=THUMB_CHOICES, default='hd')
    height = models.CharField(max_length=10, null=True, blank=True)
    width = models.CharField(max_length=10, null=True, blank=True)
    media = models.ImageField(width_field="width", height_field="height",
                              null=True, blank=True,
                              upload_to=thumbnail_location)

    def __str__(self):
        return str(self.media.path)


def create_new_thumb(media_path, instance, owner_slug, size):
    filename = os.path.basename(media_path)
    thumb = Image.open(media_path)
    thumb.thumbnail(size, Image.ANTIALIAS)

    temp_loc = "%s/%s/tmp" % (settings.MEDIA_ROOT, owner_slug)
    if not os.path.exists(temp_loc):
        os.makedirs(temp_loc)

    temp_file_path = os.path.join(temp_loc, filename)
    if os.path.exists(temp_file_path):
        temp_path = os.path.join(temp_loc, "%s" % (random.random()))
        os.makedirs(temp_path)
        temp_file_path = os.path.join(temp_path, filename)

    temp_image = open(temp_file_path, "wb")
    thumb.save(temp_image, "JPEG")
    thumb_data = open(temp_file_path, "rb")

    thumb_file = File(thumb_data)
    print("OTO filename ", filename)
    print("OTO thumb_file ", thumb_file)
    instance.media.save(filename, thumb_file)
    shutil.rmtree(temp_loc, ignore_errors=True)


# TODO check if images already exists (duplicates)
def product_post_save_receiver(sender, instance, *args, **kwargs):
    if instance.media:
        media_path = instance.media.path
        owner_slug = instance.slug
        for i in range(len(THUMB_SIZE)):
            thumb, thumb_created = Thumbnail.objects.get_or_create(product=instance,
                                                                   type=THUMB_CHOICES[i])
            if thumb_created:
                create_new_thumb(media_path, thumb, owner_slug, THUMB_SIZE[i])


post_save.connect(product_post_save_receiver, sender=Product)


# class Video(models.Model):
#     title = models.CharField(max_length=120)
#     embed_code = models.CharField(max_length=500, null=True, blank=True)
#
#     def __str__(self):
#         return self.titled