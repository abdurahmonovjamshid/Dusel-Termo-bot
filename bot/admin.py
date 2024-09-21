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


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ('machine_num', 'product', 'termoplast_measure', 'waste_measure',
                    'defect_measure', 'material', 'quantity', 'default_value')
    ordering = ('date', 'default_value')


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
