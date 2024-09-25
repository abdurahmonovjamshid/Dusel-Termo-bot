from django import forms
from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Product, Material, TgUser, Report, Machine


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('itemcode', 'name')
    ordering = ('name',)


@admin.register(Material)
class MaterialAdmin(admin.ModelAdmin):
    list_display = ('itemcode', 'name')


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ('number', 'product')


from datetime import datetime

@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('machine_num', 'product', 'termoplast_measure', 'waste_measure',
                    'defect_measure', 'material', 'quantity', 'default_value', 'date')
    ordering = ('-date', 'default_value')
    list_filter = ['date']
    
    # Correct search field for ForeignKey 'product' and related field 'name'
    search_fields = ['product__name']  # Add more fields if needed

    def get_search_results(self, request, queryset, search_term):
        # Default search fields query
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)

        # Date formats to try
        date_formats = ['%d.%m.%Y', '%d/%m/%Y', '%d-%m-%Y']

        # Try matching search_term with date formats
        for date_format in date_formats:
            try:
                search_date = datetime.strptime(search_term, date_format).date()
                queryset |= self.model.objects.filter(date=search_date)
                break  # Stop once a valid date is found
            except ValueError:
                continue  # Continue to next format if not matched

        return queryset, use_distinct




@admin.register(TgUser)
class TgUserAdmin(admin.ModelAdmin):

    list_display = ('__str__', 'phone', 'created_at')

    fieldsets = (
        ("User Information", {
            'fields': ('telegram_id', 'first_name', 'last_name', 'phone', 'username'),
        }),
        ('Additional Information', {
            'fields': ('created_at', 'step', 'deleted'),
        }),
    )

    def has_change_permission(self, *args, **kwargs):
        return False

    def has_add_permission(self, *args, **kwargs):
        return False
