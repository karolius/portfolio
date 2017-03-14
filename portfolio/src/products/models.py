import os
import shutil
import random
import uuid
from PIL import Image
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.utils.text import slugify
from django.core.files import File


THUMB_CHOICES = (("hd", "HD"),
                 ("sd", "SD"),
                 ("micro", "Micro"),)

THUMB_SIZE = ((700, 700),
              (350, 350),
              (150, 150))

STATUS_CHOICES = (("active", "Active"),
                  ("out_of_stock", "Out of stock"),
                  ("inactive", "Inactive"),)


def download_media_location(instance, filename):
    return "%s/%s" % (instance.id, filename)


class ProductQuerySet(models.QuerySet):
    def active(self):
        return self.filter(status="active")


class ProductManager(models.Manager):
    def get_queryset(self):
        return ProductQuerySet(self.model, using=self._db)

    def all(self, *args, **kwargs):
        return self.get_queryset().active()

    def get_related(self, instance):
        return self.get_queryset()\
            .filter(category__in=instance.category.all())\
            .exclude(id=instance.id)\
            .distinct()


class Product(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=120)
    description = models.TextField()
    price = models.DecimalField(max_digits=25, decimal_places=2)
    sale_price = models.DecimalField(max_digits=25, decimal_places=2,
                                     null=True, blank=True)
    sale_active = models.BooleanField(default=False)
    media = models.ImageField(upload_to=download_media_location,
                              null=True, blank=True,
                              storage=FileSystemStorage(location=settings.PROTECTED_ROOT))
    category = models.ManyToManyField("Category", blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    objects = ProductManager()

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("products:detail", kwargs={"id": self.id})

    def get_image_url(self, type="sd"):
        img = self.thumbnail_set.all()
        if img.count() > 0:
            img = img.get(type=type)
            if img is not None:
                return img.media.url
        return None


def thumbnail_location(instance, filename):
    return "%s/%s" % (instance.product.id, filename)


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
    instance.media.save(filename, thumb_file)
    shutil.rmtree(temp_loc, ignore_errors=True)


class Variation(models.Model):
    title = models.CharField(max_length=120)
    sub_description = models.CharField(max_length=360, null=True, blank=True)
    price = models.DecimalField(max_digits=25, decimal_places=2)
    sale_price = models.DecimalField(max_digits=25, decimal_places=2,
                                     null=True, blank=True)
    sale_active = models.BooleanField(default=False)
    product = models.ForeignKey(Product)

    def __str__(self):
        return self.title

    def get_price(self):
        if self.sale_price is not None:
            return self.sale_price
        return self.price

    def get_html_price(self):
        if self.sale_price is not None:
            html_text = "<h3><span class='sale-price'>%s</span>" \
                        " <small class='og-price'>%s</small></h3>" \
                        % (self.sale_price, self.price)
        else:
            html_text = "<h3 class='price'>%s</h3>" % self.price

        return mark_safe(html_text)

    def get_absolute_url(self):
        return self.product.get_absolute_url()


def product_post_save_receiver(sender, instance, *args, **kwargs):
    variations = instance.variation_set.all()
    if variations.count() == 0:
        new_variation = Variation()
        new_variation.product = instance
        new_variation.title = "Default"
        new_variation.price = instance.price
        new_variation.sale_price = instance.sale_price
        new_variation.sale_active = instance.sale_active
        new_variation.save()

    if instance.media:
        media_path = instance.media.path
        owner_id = instance.id
        for i in range(len(THUMB_SIZE)):
            thumb, thumb_created = Thumbnail.objects.get_or_create(product=instance,
                                                                   type=THUMB_CHOICES[i][0])
            if thumb_created:
                create_new_thumb(media_path, thumb, owner_id, THUMB_SIZE[i])


post_save.connect(product_post_save_receiver, sender=Product)


class Category(models.Model):
    title = models.CharField(max_length=120, unique=True)
    slug = models.SlugField(blank=True, unique=True)
    # timestamp = models.DateTimeField(auto_now_add=True, auto_now=False)

    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse("categories:detail", kwargs={"slug": self.slug})


def category_post_save_receiver(sender, instance, *args, **kwargs):
    if not instance.slug:
        instance.slug = slugify(instance.title)


post_save.connect(category_post_save_receiver, sender=Category)