from django.db import migrations, models
import django.db.models.deletion

class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('offers', '0001_initial'),
        ('orders', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Ticket',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ticket_key', models.CharField(editable=False, max_length=128, unique=True)),
                ('qr_image', models.ImageField(blank=True, null=True, upload_to='qr/')),
                ('offer', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='offers.offer')),
                ('order', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='orders.order')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='auth.user')),
            ],
        ),
    ]
