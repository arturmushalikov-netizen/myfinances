import datetime

from django.utils import timezone
from django.db import models
from django.contrib import admin
import pgtrigger

class MonthlyFin(models.Model):
    month_text = models.CharField(max_length=200)
    start_date = models.DateField("start of period")
    end_date = models.DateField("end of period")
    summ = models.FloatField(default=0)

    def __str__(self):
        return self.month_text
    @admin.display(
        boolean=True,
        ordering="start_date",
        )
    def last_montly_fin(self):
        return self.start_date <= timezone.now().date() <= self.end_date
    
    class Meta:
        get_latest_by = "-end_date"

class MonthList(models.Model):
    month = models.ForeignKey(MonthlyFin, on_delete=models.CASCADE)
    check_date = models.DateTimeField("date of purchase", default=timezone.now)
    check_price = models.FloatField(default=0)

    class Meta:
        triggers = [
            pgtrigger.Trigger(
                name="MonthList_INS_Trigger",
                operation=pgtrigger.Insert,
                when=pgtrigger.After,
                func="""
                    UPDATE MYFINANCES_MONTHLYFIN
                    SET SUMM = (SELECT SUM(CHECK_PRICE)
                                FROM MYFINANCES_MONTHLIST as ML
                                WHERE ML.MONTH_ID = NEW.MONTH_ID)
                    WHERE ID = NEW.MONTH_ID;
                    RETURN NEW;
                """,
            )
        ]

    def __str__(self):
        return self.check_date.strftime("%Y-%m-%d %H:%M")