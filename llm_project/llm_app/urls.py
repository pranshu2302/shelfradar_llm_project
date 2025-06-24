from rest_framework.routers import DefaultRouter
from .views import (
    DatasetViewSet,
    PromptTemplateViewSet,
    EvaluationViewSet,
)

router = DefaultRouter()
router.register(r'datasets', DatasetViewSet, basename='dataset')
router.register(r'prompts', PromptTemplateViewSet, basename='prompt')
router.register(r'evaluations', EvaluationViewSet, basename='evaluation')
urlpatterns = router.urls


