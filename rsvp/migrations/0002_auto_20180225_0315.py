# Generated by Django 2.0.2 on 2018-02-25 03:15

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('rsvp', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ignite',
            name='invitation',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='rsvp.Invitation'),
        ),
        migrations.AlterField(
            model_name='plusone',
            name='invitation',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='rsvp.Invitation'),
        ),
        migrations.AlterField(
            model_name='roommate',
            name='invitation',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='rsvp.Invitation'),
        ),
        migrations.AlterField(
            model_name='session',
            name='invitation',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='rsvp.Invitation'),
        ),
        migrations.AlterField(
            model_name='stipend',
            name='cost_estimate',
            field=models.IntegerField(blank=True, help_text="How much do you estimate air and ground transportation will cost? Don't include lodging and meals. (Just numbers, no dollar signs or symbols.)", null=True),
        ),
    ]
