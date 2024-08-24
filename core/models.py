from django.db import models


class VolatilityChat(models.Model):
    date = models.DateField(db_column='Date', blank=True, null=True)
    time = models.TimeField(db_column='Time', blank=True, null=True)
    open = models.DecimalField(db_column='Open', max_digits=10, decimal_places=4, blank=True, null=True)
    high = models.DecimalField(db_column='High', max_digits=10, decimal_places=4, blank=True, null=True)
    low = models.DecimalField(db_column='Low', max_digits=10, decimal_places=4, blank=True, null=True)
    close = models.DecimalField(db_column='Close', max_digits=10, decimal_places=4, blank=True, null=True)
    indicator1_on_chart = models.DecimalField(db_column='Indicator1_OnChart', max_digits=10, decimal_places=4, blank=True, null=True)
    indicator2_on_chart = models.DecimalField(db_column='Indicator2_OnChart', max_digits=10, decimal_places=4, blank=True, null=True)
    indicator1_in_pane_below = models.DecimalField(db_column='Indicator1_InPaneBelow', max_digits=10, decimal_places=3, blank=True, null=True)
    symbol = models.CharField(max_length=100, blank=True, null=True, db_column='SYMBOL')



    class Meta:
        verbose_name_plural = 'VolatilityChat'
        managed = False
        abstract = True


    def __str__(self):
        return f"{self.date} {self.time}"

    @classmethod
    def for_table(cls, table_name):
        return type(f'VolatilityChat_{table_name}', (cls,), {
            '__module__': cls.__module__,
            'Meta': type('Meta', (), {
                'db_table': table_name,
                'managed': False
            })
        })
