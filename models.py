from django.db import models

class ComputationStatus(models.Model):
    group_id = models.CharField(max_length=100, verbose_name="Group ID")
    create_stage = models.CharField(max_length=100, verbose_name="Create")
    setup_stage = models.CharField(max_length=100, verbose_name="Setup")
    run_stage = models.CharField(max_length=100, verbose_name="Run")
    terminate_stage = models.CharField(max_length=100, verbose_name="Terminate")

    def __unicode__(self):
        return self.group_id

