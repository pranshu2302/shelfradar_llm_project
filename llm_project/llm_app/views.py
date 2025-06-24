from .models import Dataset,PromptTemplate,Evaluation,EvaluationResult
from .serializers import DatasetSerializer,PromptTemplateSerializer,EvaluationSerializer
from rest_framework import viewsets,status
from rest_framework.decorators import action
from rest_framework.response import Response
from .utils import render_prompt
from .tasks import run_evaluation
from django.db.models import Avg

class DatasetViewSet(viewsets.ModelViewSet):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

class PromptTemplateViewSet(viewsets.ModelViewSet):
    queryset = PromptTemplate.objects.all().order_by('-created_at')
    serializer_class = PromptTemplateSerializer

    @action(detail=True, methods=['post'], url_path='render')
    def render_with_data(self, request, pk=None):
        template = self.get_object()
        data = request.data.get("row", {})
        if not isinstance(data, dict):
            return Response({"error": "Invalid 'row' format. Expected a JSON object."}, status=status.HTTP_400_BAD_REQUEST)

        rendered = render_prompt(template.template, data)
        return Response({"rendered_prompt": rendered})
    
class EvaluationViewSet(viewsets.ModelViewSet):
    queryset = Evaluation.objects.all().order_by('-created_at')
    serializer_class = EvaluationSerializer

    @action(detail=True, methods=['post'], url_path='run')
    def run_evaluation_task(self, request, pk=None):
        evaluation = self.get_object()
        run_evaluation.delay(evaluation.id)
        return Response({
            "message": f"Evaluation #{evaluation.id} has been queued.",
            "evaluation_id": evaluation.id
        }, status=status.HTTP_202_ACCEPTED)
    
    @action(detail=True, methods=['get'], url_path='aggregates')
    def evaluation_aggregates(self, request, pk=None):
        evaluation = self.get_object()

        # Group by llm_name and aggregate scores
        results = (
        EvaluationResult.objects
        .filter(evaluation=evaluation)
        .values('llm_name')
        .annotate(
            avg_correctness=Avg('correctness'),
            avg_faithfulness=Avg('faithfulness')
        )
    )

        llm_aggregates = {
            result['llm_name']: {
                'correctness_avg': round(result['avg_correctness'], 2) if result['avg_correctness'] else None,
                'faithfulness_avg': round(result['avg_faithfulness'], 2) if result['avg_faithfulness'] else None,
            }
            for result in results
        }

        return Response({
            'evaluation_id': evaluation.id,
            'llm_aggregates': llm_aggregates
        }, status=status.HTTP_200_OK)