from django.db import models


class Category(models.Model):
    name = models.CharField(max_length=100)


class Mode(models.Model):
    name = models.CharField(max_length=100)


class JobOffer(models.Model):
    title = models.CharField(max_length=255)
    description = models.CharField()
    location = models.CharField(max_length=100)
    company = models.CharField(max_length=100)
    date_publication = models.CharField(max_length=100)
    link = models.CharField(max_length=500, default='')
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    mode = models.ForeignKey(Mode, on_delete=models.CASCADE)


class Responsibility(models.Model):
    description = models.CharField()
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE)


class Requirement(models.Model):
    description = models.CharField()
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE)


class Availability(models.Model):
    description = models.CharField()
    job_offer = models.ForeignKey(JobOffer, on_delete=models.CASCADE)


