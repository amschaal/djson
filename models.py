from django.db import models
from django.contrib.contenttypes.models import ContentType


class DjsonModelBase(models.Model):
    class Meta:
        abstract = True
    def validate(self):
        pass

class ModelType(models.Model):
    class Meta:
        # abstract = True
        unique_together = (('content_type', 'name'))
    id = models.CharField(primary_key=True, max_length=30)
    content_type = models.ForeignKey(ContentType, on_delete=models.RESTRICT)
    name = models.CharField(max_length=50)
    description = models.TextField()
    schema = models.JSONField(default=dict)

class DjsonModel(DjsonModelBase):
    class Meta:
        abstract = True
    data = models.JSONField(default=dict)
    schema = models.JSONField(default=dict)


class DjsonTypeModel(DjsonModel):
    class Meta:
        abstract = True
    type = models.ForeignKey(ModelType, null=True, on_delete=models.RESTRICT)
    data = models.JSONField(default=dict)
    schema = models.JSONField(default=dict)