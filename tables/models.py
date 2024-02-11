from django.db import models
from django.contrib.auth.models import User

class Database(models.Model):
    def jsonfield_default_value(): return []    

    name = models.CharField(max_length=255, unique=True)
    allowed_origins = models.JSONField(default=jsonfield_default_value, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='databases')


class TableBluePrint(models.Model):
    name = models.CharField(max_length=255)
    database = models.ForeignKey(Database, on_delete=models.CASCADE, related_name='tables')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='tables')

class TableFieldBluePrint(models.Model):
    character = 'char'
    integer = 'int'
    boolean = 'bool'
    json = 'json'
    text = 'text'
    FIELD_TYPE_CHOICES = [
       (character, 'Character'),
       (integer, 'Integer'),
       (json, 'JSON'),
       (boolean, 'Boolean'),
       (text, 'Text'),
    ]
    name = models.CharField(max_length=255)
    blank = models.BooleanField(default=False)
    unique = models.BooleanField(default=False)
    has_default = models.BooleanField(default=False)
    default_text_field = models.TextField(blank=True)
    default_character_field = models.CharField(max_length=255, blank=True)
    default_integer_field = models.IntegerField(blank=True, null=True)
    default_boolean_field = models.BooleanField(blank=True, null=True)
    default_JSON_field = models.JSONField(blank=True, null=True)
    type = models.CharField(choices=FIELD_TYPE_CHOICES, max_length=9)
    table_blue_print = models.ForeignKey(TableBluePrint, on_delete=models.CASCADE,related_name='fields')

class TableInstance(models.Model):
    table_blue_print = models.ForeignKey(TableBluePrint, related_name='table_instances',on_delete=models.CASCADE)

class TableInstanceField(models.Model):
    table_instance = models.ForeignKey(TableInstance, related_name='fields', on_delete=models.CASCADE)
    table_field_blue_print = models.ForeignKey(TableFieldBluePrint,  related_name='table_instance_fields', on_delete=models.CASCADE)
    text_field = models.TextField(blank=True)
    character_field = models.CharField(max_length=255, blank=True)
    integer_field = models.IntegerField(blank=True, null=True)
    boolean_field = models.BooleanField(blank=True, null=True)
    JSON_field = models.JSONField(blank=True, null=True)

class Dummy(models.Model):
    name = models.CharField(max_length=255, blank=True, unique=True)


