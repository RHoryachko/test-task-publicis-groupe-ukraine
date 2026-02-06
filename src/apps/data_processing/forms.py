from django import forms


class DataFileUploadForm(forms.Form):
    file = forms.FileField(
        label="Файл даних (xls/csv)",
        help_text="Колонки: Advertis, Brand, Start, End, Format, Platform, Impr. Start та End не повинні бути порожніми.",
        widget=forms.FileInput(attrs={"accept": ".xls,.xlsx,.csv"}),
    )
