# Generated by Django 3.2.4 on 2021-06-24 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [("base", "0003_auto_20200226_1152")]

    operations = [
        migrations.AlterField(
            model_name="news",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
        migrations.AlterField(
            model_name="system",
            name="id",
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]