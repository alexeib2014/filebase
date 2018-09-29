# Generated by Django 2.1.1 on 2018-09-29 08:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('import', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Disk',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('file_datetime', models.DateTimeField()),
                ('create_datetime', models.DateTimeField()),
                ('comment', models.TextField()),
            ],
        ),
        migrations.AlterField(
            model_name='folder',
            name='disk',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='import.Disk'),
        ),
        migrations.DeleteModel(
            name='Disc',
        ),
    ]