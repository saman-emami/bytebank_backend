# Generated by Django 4.2.5 on 2023-10-15 17:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import tables.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Database',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('allowed_origins', models.JSONField(blank=True, default=tables.models.Database.jsonfield_default_value)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='databases', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Dummy',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='TableBluePrint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('database', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tables', to='tables.database')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tables', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TableFieldBluePrint',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('blank', models.BooleanField(default=False)),
                ('unique', models.BooleanField(default=False)),
                ('has_default', models.BooleanField(default=False)),
                ('default_text_field', models.TextField(blank=True)),
                ('default_character_field', models.CharField(blank=True, max_length=255)),
                ('default_integer_field', models.IntegerField(blank=True, null=True)),
                ('default_boolean_field', models.BooleanField(blank=True, null=True)),
                ('default_JSON_field', models.JSONField(blank=True, null=True)),
                ('type', models.CharField(choices=[('char', 'Character'), ('int', 'Integer'), ('json', 'JSON'), ('bool', 'Boolean'), ('text', 'Text')], max_length=9)),
                ('table_blue_print', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='tables.tableblueprint')),
            ],
        ),
        migrations.CreateModel(
            name='TableInstance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('table_blue_print', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='table_instances', to='tables.tableblueprint')),
            ],
        ),
        migrations.CreateModel(
            name='TableInstanceField',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('text_field', models.TextField(blank=True)),
                ('character_field', models.CharField(blank=True, max_length=255)),
                ('integer_field', models.IntegerField(blank=True, null=True)),
                ('boolean_field', models.BooleanField(blank=True, null=True)),
                ('JSON_field', models.JSONField(blank=True, null=True)),
                ('table_field_blue_print', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='table_instance_fields', to='tables.tablefieldblueprint')),
                ('table_instance', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='tables.tableinstance')),
            ],
        ),
    ]
