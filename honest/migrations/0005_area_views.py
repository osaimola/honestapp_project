# Generated by Django 2.0 on 2019-02-20 13:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('honest', '0004_auto_20190219_2133'),
    ]

    operations = [
        migrations.AddField(
            model_name='area',
            name='views',
            field=models.IntegerField(default=0),
        ),
    ]
