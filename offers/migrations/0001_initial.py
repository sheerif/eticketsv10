from django.db import migrations, models

class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('offer_type', models.CharField(choices=[('solo', 'Solo'), ('duo', 'Duo'), ('familiale', 'Familiale')], max_length=16)),
                ('description', models.TextField(blank=True)),
                ('price_eur', models.DecimalField(decimal_places=2, max_digits=8)),
                ('is_active', models.BooleanField(default=True)),
            ],
        ),
    ]
