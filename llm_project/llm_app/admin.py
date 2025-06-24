from django.contrib import admin
from .models import Dataset,PromptTemplate,Evaluation,EvaluationResult

@admin.register(Dataset)
class DatasetAdmin(admin.ModelAdmin):
    list_display = ("name", "uploaded_at")
    readonly_fields = ("uploaded_at",)

@admin.register(PromptTemplate)
class PromptTemplateAdmin(admin.ModelAdmin):
    list_display = ("name", "created_at")
    readonly_fields = ("created_at",)

@admin.register(Evaluation)
class EvaluationAdmin(admin.ModelAdmin):
    list_display = ("id", "dataset", "prompt_template", "created_at")
    readonly_fields = ("created_at",)
    search_fields = ("dataset__name", "prompt_template__name")
    list_filter = ("created_at",)

@admin.register(EvaluationResult)
class EvaluationResultAdmin(admin.ModelAdmin):
    list_display = ("evaluation", "row_index", "llm_name", "correctness", "faithfulness")
    search_fields = ("llm_name", "evaluation__id")
    list_filter = ("llm_name", "evaluation")