# Generated by Django 3.0.9 on 2020-09-06 17:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('profiles', '0005_relation_block'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relation',
            name='status',
            field=models.CharField(choices=[('send', 'send'), ('accepted', 'accepted')], max_length=8, null=True),
        ),
    ]
