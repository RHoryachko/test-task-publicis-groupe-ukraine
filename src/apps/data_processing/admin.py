from django.contrib import admin
from .models import DataFile, DataRecord


@admin.register(DataFile)
class DataFileAdmin(admin.ModelAdmin):
    """
    Admin panel for uploaded files.
    """
    list_display = (
        'filename',
        'get_user_email',
        'uploaded_at',
        'status',
        'error_type',
        'rows_processed',
        'file_size'
    )
    list_filter = ('status', 'error_type', 'uploaded_at')
    search_fields = ('filename', 'user__email', 'user__username')
    readonly_fields = ('uploaded_at', 'file_size')
    date_hierarchy = 'uploaded_at'
    
    fieldsets = (
        ('Файл', {
            'fields': ('user', 'filename', 'file_size')
        }),
        ('Статус', {
            'fields': ('status', 'error_type', 'error_message')
        }),
        ('Статистика', {
            'fields': ('rows_processed',)
        }),
        ('Дата', {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_user_email(self, obj):
        """Get user email."""
        return obj.user.email
    get_user_email.short_description = 'User email'
    get_user_email.admin_order_field = 'user__email'
    
    def get_queryset(self, request):
        """Optimization of requests."""
        return super().get_queryset(request).select_related('user')


@admin.register(DataRecord)
class DataRecordAdmin(admin.ModelAdmin):
    """Admin panel for data records."""
    list_display = (
        'id',
        'get_file_name',
        'advertiser',
        'brand',
        'start_date',
        'end_date',
        'platform',
        'impressions',
        'year'
    )
    list_filter = ('year', 'platform', 'format_type', 'file__uploaded_at')
    search_fields = (
        'advertiser',
        'brand',
        'platform',
        'file__filename'
    )
    readonly_fields = ('created_at',)
    date_hierarchy = 'start_date'
    
    fieldsets = (
        ('Файл', {
            'fields': ('file',)
        }),
        ('Основні дані', {
            'fields': (
                'advertiser',
                'brand',
                'start_date',
                'end_date',
                'year'
            )
        }),
        ('Реклама', {
            'fields': ('format_type', 'platform', 'impressions')
        }),
        ('Метадані', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_file_name(self, obj):
        """Get file name."""
        return obj.file.filename
    get_file_name.short_description = 'Файл'
    get_file_name.admin_order_field = 'file__filename'
    
    def get_queryset(self, request):
        """Оптимізація запитів."""
        return super().get_queryset(request).select_related('file')
