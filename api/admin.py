from django.contrib import admin
from core.models import Note, Category
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "note_count")
    search_fields = ("name",)

    def note_count(self, obj):
        return obj.note_set.count()

    note_count.short_description = "Número de Notas"


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ("title", "category_link", "owner_link", "created_at", "updated_at")
    list_filter = ("category", "owner", "created_at")
    search_fields = ("title", "content", "category__name", "owner__username")
    readonly_fields = ("created_at", "updated_at")
    actions = ["duplicate_note"]

    fieldsets = (
        (None, {"fields": ("title", "content", "category", "owner")}),
        ("Datas", {"fields": ("created_at", "updated_at"), "classes": ("collapse",)}),
    )

    def category_link(self, obj):
        if obj.category:
            url = reverse("admin:core_category_change", args=[obj.category.id])
            return format_html('<a href="{}">{}</a>', url, obj.category.name)
        return "-"

    category_link.short_description = "Categoria"

    def owner_link(self, obj):
        url = reverse("admin:auth_user_change", args=[obj.owner.id])
        return format_html('<a href="{}">{}</a>', url, obj.owner.username)

    owner_link.short_description = "Proprietário"

    def duplicate_note(self, request, queryset):
        for note in queryset:
            note.pk = None
            note.title = f"Cópia de {note.title}"
            note.save()
        self.message_user(
            request, f"{queryset.count()} nota(s) duplicada(s) com sucesso."
        )

    duplicate_note.short_description = "Duplicar nota(s) selecionada(s)"

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(owner=request.user)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "owner" and not request.user.is_superuser:
            kwargs["queryset"] = User.objects.filter(id=request.user.id)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):
        if not obj.pk and not request.user.is_superuser:
            obj.owner = request.user
        super().save_model(request, obj, form, change)