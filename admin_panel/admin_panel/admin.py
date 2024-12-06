import os
import logging
from django import forms
from django.urls import reverse
from django.contrib import admin
from django.shortcuts import render, redirect
from django.core.files.storage import default_storage
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from openpyxl import Workbook
from typing import Optional
from asgiref.sync import async_to_sync
from django.urls import path

from .models import User, Product, Cart, Category, FAQ
from bot.main import get_bot
from utils.tl_utils import send_message_to_telegram
from config import settings


logger = logging.getLogger(__name__)


class SendMessageForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea, required=True, label="Message Text")
    photo = forms.ImageField(required=False, label="Attach a Photo")


class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "first_name", "last_name", "username", "lang")
    list_per_page = 50
    actions = ["send_message_to_users"]

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "send-message/",
                self.admin_site.admin_view(self.send_message_form_view),
                name="send_message_form",
            ),
        ]
        return custom_urls + urls

    def send_message_to_users(self, request, queryset):
        user_ids = queryset.values_list("id", flat=True)
        user_ids_str = ",".join(map(str, user_ids))
        url = reverse("admin:send_message_form")

        url_with_params = f"{url}?user_ids={user_ids_str}"

        return redirect(url_with_params)

    def send_message_form_view(self, request):
        user_ids = request.GET.get("user_ids", "").split(",")
        users = User.objects.filter(id__in=user_ids)

        form = SendMessageForm(request.POST or None, request.FILES or None)

        if request.method == "POST" and form.is_valid():
            text = form.cleaned_data["text"]
            photo = form.cleaned_data.get("photo")

            logger.info(f"Selected users: {users}, Text: {text}, Photo: {photo}")

            photo_path = None
            if photo:
                photo_path = default_storage.save("mailings/" + photo.name, photo)
                logger.info(f"Photo uploaded and saved at: {photo_path}")

            photo_path = os.path.join(
                os.getcwd(), "admin_panel/media/mailings", photo.name
            )
            for user in users:
                async_to_sync(self.send_message_to_telegram)(user, text, photo_path)

            # After sending the messages, notify and redirect
            self.message_user(request, "Messages sent successfully!")
            return redirect(
                "admin:admin_panel_user_changelist"
            )  # Adjust this as necessary

        return render(request, "send_message_form.html", {"form": form, "users": users})

    @staticmethod
    async def send_message_to_telegram(user: User, text: str, photo: str):
        logger.info(f"{user}")
        await send_message_to_telegram(get_bot(), user.id, text, photo)

    send_message_to_users.short_description = "Send a message with text and photo"


class CartAdmin(admin.ModelAdmin):
    actions = ["download_excel"]

    def download_excel(self, request, queryset) -> Optional[HttpResponse]:
        if not os.path.exists(settings.EXCEL_FILE_PATH):
            wb = Workbook()
            ws = wb.active
            ws.title = "Cart"

            headers = [
                "ID",
                "User",
                "Product Name",
                "Amount",
                "Cost",
                "Address",
                "Is Being Delivered",
            ]
            ws.append(headers)

            for cart_item in queryset:
                row = [
                    cart_item.id,
                    cart_item.user.username if cart_item.user else "Unknown",
                    cart_item.product_name,
                    cart_item.amount,
                    cart_item.cost,
                    cart_item.address or "Not provided",
                    "Yes" if cart_item.is_being_delivered else "No",
                ]
                ws.append(row)

            os.makedirs(os.path.dirname(settings.EXCEL_FILE_PATH), exist_ok=True)
            wb.save(settings.EXCEL_FILE_PATH)
            self.message_user(
                request,
                f"Excel file created at {settings.EXCEL_FILE_PATH}",
                level="success",
            )

        with open(settings.EXCEL_FILE_PATH, "rb") as file:
            response = HttpResponse(
                file.read(),
                content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
            response["Content-Disposition"] = (
                f"attachment; filename={os.path.basename(settings.EXCEL_FILE_PATH)}"
            )
            return response


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'cost', 'amount', 'image_preview')
    list_filter = ("category",)
    search_fields = ("name",)

    def image_preview(self, obj):
        if obj.photo:
            return mark_safe(f'<img src="{obj.photo.url}" width="50" height="50" />')
        return 'No image'

    image_preview.short_description = 'Image Preview'


admin.site.register(User, UserAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(Category)
admin.site.register(FAQ)

admin.site.site_header = "Admin panel"
admin.site.site_title = "Admin panel"
