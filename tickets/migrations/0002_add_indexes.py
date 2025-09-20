# Generated migration for database optimization
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('tickets', '0001_initial'),
    ]

    operations = [
        # Add index on ticket_key for fast verification lookups
        migrations.AlterField(
            model_name='ticket',
            name='ticket_key',
            field=models.CharField(
                max_length=128, 
                unique=True, 
                editable=False,
                db_index=True,  # Add database index
                help_text="Unique ticket key with checksum for verification"
            ),
        ),
        # Add composite index for user + order queries
        migrations.AlterModelOptions(
            name='ticket',
            options={'indexes': [
                models.Index(fields=['user', 'order'], name='tickets_user_order_idx'),
                models.Index(fields=['order', 'offer'], name='tickets_order_offer_idx'),
            ]},
        ),
    ]