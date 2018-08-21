from django.db import models


class FeedModel(models.Model):
    id = models.CharField(max_length=200, primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    link = models.CharField(max_length=200)
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_time']

    def __str__(self):
        return self.title
