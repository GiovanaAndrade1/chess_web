from django.db import migrations, models
from django.db.models.functions import Length

def verificar_emails(apps, schema_editor):
    Usuario = apps.get_model('chess_web', 'Usuario')
    usuarios = Usuario.objects.using(schema_editor.connection.alias).annotate(tamanho=Length('email')).filter(tamanho__gt=254)
    if usuarios.exists():
        raise RuntimeError('Existem emails maiores que 254 caracteres. Corrija-os antes de migrar; nenhum email será truncado.')

class Migration(migrations.Migration):
    dependencies = [('chess_web', '0012_alter_partida_torneios_alter_partida_torneio')]
    operations = [
        migrations.RunPython(verificar_emails, migrations.RunPython.noop),
        migrations.AlterField(model_name='usuario', name='email', field=models.EmailField(max_length=254, unique=True)),
    ]
