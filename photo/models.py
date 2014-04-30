#-*- encoding: utf-8 -*-

from django.db import models
from django import forms
# from django.conf import settings
from django.core.files.storage import FileSystemStorage
from django_thumbs.db.models import ImageWithThumbsField
from member.models import Member
from django.db.models.signals import pre_save

from PIL import Image
import os


class Album(models.Model):
    pub_date = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="投稿日時")
    title = models.CharField(max_length=200, blank=False, verbose_name="タイトル")
    author = models.ForeignKey(Member, blank=True, null=True, default=None)
    message = models.TextField(blank=False, verbose_name="本文")

    class Meta:
        verbose_name = verbose_name_plural = 'アルバム'

    def __unicode__(self):
        return self.title



class Photo(models.Model):
    album = models.ForeignKey(Album)
    pub_date = models.DateTimeField(auto_now_add=True, editable=False, verbose_name="投稿日時")
    title = models.CharField(max_length=200, blank=False, verbose_name="タイトル")
    author = models.ForeignKey(Member, related_name='author')
    message = models.TextField(blank=False, verbose_name="本文")
    member = models.ManyToManyField(Member, blank=True, related_name='member')
    image = models.ImageField(upload_to='photo', verbose_name="写真")
    thumb = models.ImageField(upload_to='photo', editable=False, verbose_name="サムネイル")


    class Meta:
        verbose_name = verbose_name_plural = '写真'

    def __unicode__(self):
        return self.title

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        # if self.image and not os.path.exists(self.image.path):
        if self.image:
            from cStringIO import StringIO

            self.image.open('r+b')

            a = self.image.read()
            im = Image.open(StringIO(a))
            # self.image.close()
            y = im.size[0] > im.size[1]
            if y:
                l = im.size[0]
                s = im.size[1]
            else:
                s = im.size[0]
                l = im.size[1]

            new_size = 1920
            if l > new_size:
                a = new_size * s / l
                im.thumbnail(y and (new_size, a) or (a, new_size), Image.ANTIALIAS)
                print 'resize'

            fp = StringIO()
            im.save(fp, format=im.format)

            self.image.truncate(0)
            self.image.seek(0)
            self.image.write(fp.getvalue())

            # self.image.close()
            fp.close()

        root, ext = os.path.splitext(self.image.path)

        thumb_filename = '%s-thumb%s' % (root, ext)

        y = im.size[0] > im.size[1]
        if y:
            l = im.size[0]
            s = im.size[1]
        else:
            s = im.size[0]
            l = im.size[1]

        thumb_size = 200

        if l > thumb_size:
            a = thumb_size * l / s
            im.resize(y and (a, thumb_size) or (thumb_size, a), Image.ANTIALIAS).save(thumb_filename)

        r = super(Photo, self).save(force_insert, force_update, using, update_fields)
        return r




#pre_save.connect(pre_save_photo, sender=Photo)
