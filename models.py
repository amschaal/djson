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
    # category = models.SlugField(null=True)
    name = models.CharField(max_length=50)
    description = models.TextField()
    schema = models.JSONField(default=dict)
    metadata = models.JSONField(default=dict) # store other useful information for your app
    @classmethod
    def get_model_queryset(cls, model_class: models.Model):
        return cls.objects.filter(content_type=ContentType.objects.get_for_model(model_class))
    @classmethod
    def get_model_choices(cls, model_class: models.Model):
        return ((mt.id, mt.name) for mt in cls.get_model_queryset(model_class=model_class))

class DjsonModel(DjsonModelBase):
    class Meta:
        abstract = True
    data = models.JSONField(default=dict)
    schema = models.JSONField(default=dict)

class DjsonTypeModel(DjsonModel):
    class Meta:
        abstract = True
    type = models.ForeignKey(ModelType, null=True, blank=True, on_delete=models.RESTRICT)
    data = models.JSONField(default=dict)
    schema = models.JSONField(default=dict)
    def save(self, **kwargs):
        if not self.schema and self.type and self.type.schema:
            self.schema = self.type.schema
        return super().save(**kwargs)
