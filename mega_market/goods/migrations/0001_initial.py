# Generated by Django 2.2.16 on 2022-06-19 06:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ShopUnit',
            fields=[
                ('id', models.TextField(max_length=36, primary_key=True, serialize=False)),
                ('name', models.TextField(max_length=255)),
                ('date', models.DateTimeField()),
                ('type', models.TextField(choices=[('OFFER', 'OFFER'), ('CATEGORY', 'CATEGORY')], max_length=8)),
                ('price', models.IntegerField(null=True)),
                ('parent_id', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='children', to='goods.ShopUnit')),
            ],
            options={
                'abstract': False,
            },
        ),
    ]