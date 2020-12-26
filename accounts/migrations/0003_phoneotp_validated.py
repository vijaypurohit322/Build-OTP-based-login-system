# Generated by Django 3.0.8 on 2020-09-06 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_phoneotp'),
    ]

    operations = [
        migrations.AddField(
            model_name='phoneotp',
            name='validated',
            field=models.BooleanField(default=False, help_text='If it is true, that means user validate otp correctly in second API'),
        ),
    ]
