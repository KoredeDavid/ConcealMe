# Generated by Django 3.0.5 on 2021-05-13 23:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('anon', '0008_messages_ip_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messages',
            name='ip_address',
            field=models.GenericIPAddressField(default='127.0.0.1'),
        ),
    ]