# Generated by Django 4.1.7 on 2023-04-14 13:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chess_web', '0007_delete_candidatos_usuario_descricao_usuario_facebook_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='torneios',
            name='data',
            field=models.CharField(max_length=10),
        ),
    ]