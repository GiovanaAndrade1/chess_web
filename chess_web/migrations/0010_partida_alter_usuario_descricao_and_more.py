# Generated by Django 4.2.1 on 2023-05-14 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chess_web', '0009_torneios_premio_primeiro_torneios_premio_segundo_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Partida',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('usuario_branca', models.CharField(max_length=1000)),
                ('usuario_preta', models.CharField(max_length=1000)),
                ('torneio', models.CharField(max_length=200)),
                ('vencedor', models.CharField(max_length=1)),
                ('data_partida', models.DateField()),
                ('rodada', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='usuario',
            name='descricao',
            field=models.CharField(blank=True, max_length=2000),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='facebook',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='instagram',
            field=models.CharField(blank=True, max_length=1000),
        ),
        migrations.AlterField(
            model_name='usuario',
            name='twitter',
            field=models.CharField(blank=True, max_length=1000),
        ),
    ]
