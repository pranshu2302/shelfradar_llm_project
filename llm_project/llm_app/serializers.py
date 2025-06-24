from rest_framework import serializers
from .models import Dataset,PromptTemplate,Evaluation,EvaluationResult
import pandas as pd

class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = '__all__'

    def validate_file(self, file):
        if not file.name.endswith('.csv'):
            raise serializers.ValidationError("Only CSV files are allowed.")
        
        try:
            df = pd.read_csv(file)
        except Exception as e:
            raise serializers.ValidationError(f"Invalid CSV format: {str(e)}")

        if df.shape[1] == 0:
            raise serializers.ValidationError("CSV must have at least one column.")

        if df.shape[0] == 0:
            raise serializers.ValidationError("CSV must have at least one data row.")

        return file

class PromptTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PromptTemplate
        fields = '__all__'

class EvaluationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Evaluation
        fields = '__all__'

class EvaluationResultSerializer(serializers.ModelSerializer):
    class Meta:
        model = EvaluationResult
        fields = '__all__'

