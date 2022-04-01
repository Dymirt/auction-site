# Generated by Django 4.0 on 2022-03-31 22:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auctions', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='listing',
            name='winner',
            field=models.ForeignKey(blank=True, default=None, on_delete=django.db.models.deletion.SET_DEFAULT, related_name='victories', to='auctions.user'),
        ),
    ]
