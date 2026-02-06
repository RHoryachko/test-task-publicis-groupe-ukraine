from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class DataFile(models.Model):
    _STATUS_CHOICES = [
        ('success', 'Success'),
        ('error', 'Error'),
        ('processing', 'Processing'),
    ]
    
    _ERROR_TYPE_CHOICES = [
        ('validation', 'Validation error'),
        ('format', 'Invalid file format'),
        ('structure', 'Invalid data structure'),
        ('required_columns', 'Missing required columns'),
        ('empty_dates', 'Empty values in Start/End columns'),
        ('date_format', 'Invalid date format'),
        ('date_logic', 'Start > End'),
        ('numeric', 'Error in numeric columns'),
        ('other', 'Other error'),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='uploaded_files',
        verbose_name='User'
    )
    filename = models.CharField(
        max_length=255,
        verbose_name='File name'
    )
    uploaded_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Upload date'
    )
    status = models.CharField(
        max_length=20,
        choices=_STATUS_CHOICES,
        default='processing',
        verbose_name='Upload status'
    )
    error_type = models.CharField(
        max_length=30,
        choices=_ERROR_TYPE_CHOICES,
        null=True,
        blank=True,
        verbose_name='Error type'
    )
    error_message = models.TextField(
        null=True,
        blank=True,
        verbose_name='Error message'
    )
    file_size = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='File size (bytes)'
    )
    rows_processed = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Number of processed rows'
    )
    skipped_rows_log = models.TextField(
        blank=True,
        default='',
        verbose_name='Лог пропущених рядків (Start > End)'
    )
    
    class Meta:
        verbose_name = 'Uploaded file'
        verbose_name_plural = 'Uploaded files'
        db_table = 'data_processing_data_file'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['user', '-uploaded_at']),
            models.Index(fields=['status']),
            models.Index(fields=['error_type']),
        ]
    
    def __str__(self):
        return f"{self.filename} - {self.get_status_display()}"


class DataRecord(models.Model):
    """
    Individual records from uploaded files
    """
    file = models.ForeignKey(
        DataFile,
        on_delete=models.CASCADE,
        related_name='records',
        verbose_name='File'
    )
    year = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='Year'
    )
    advertiser = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Advertiser'
    )
    brand = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name='Brand'
    )
    start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='Start date'
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name='End date'
    )
    format_type = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Format'
    )
    platform = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Platform'
    )
    impressions = models.DecimalField(
        max_digits=20,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name='Impressions'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Created at'
    )
    
    class Meta:
        verbose_name = 'Data record'
        verbose_name_plural = 'Data records'
        db_table = 'data_processing_data_record'
        ordering = ['file', 'start_date']
        indexes = [
            models.Index(fields=['file', 'year']),
            models.Index(fields=['year']),
            models.Index(fields=['start_date', 'end_date']),
            models.Index(fields=['advertiser', 'brand']),
        ]
    
    def __str__(self):
        return f"Data record {self.id} from {self.file.filename} ({self.year})"
