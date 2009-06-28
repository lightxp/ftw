from django.db import models

# Create your models here.

class Events(models.Model):
    file_name = models.CharField(max_length=200)
    date = models.DateTimeField(auto_now = True, auto_now_add = True)
    state = models.BooleanField()
    
    def __unicode__(self):
        return u"%s /%s" % (self.date, self.state)
    
    class Meta:
        verbose_name_plural = "Zdarzenia"    