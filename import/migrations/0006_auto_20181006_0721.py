# Generated by Django 2.1.1 on 2018-10-06 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('import', '0005_folder_parent'),
    ]

    operations = [
        migrations.AlterField(
            model_name='disk',
            name='name',
            field=models.CharField(db_index=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='disk',
            name='scan_datetime',
            field=models.DateTimeField(db_index=True),
        ),
        migrations.AlterField(
            model_name='file',
            name='name',
            field=models.CharField(db_index=True, max_length=200),
        ),
        migrations.AlterField(
            model_name='file',
            name='sha1sum',
            field=models.CharField(db_index=True, max_length=40),
        ),
        migrations.AlterField(
            model_name='file',
            name='size',
            field=models.IntegerField(db_index=True),
        ),
        migrations.AlterField(
            model_name='folder',
            name='name',
            field=models.CharField(db_index=True, max_length=200),
        ),
    ]