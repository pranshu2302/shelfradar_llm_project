from django.db import models

# Create your models here.
class Dataset(models.Model):
    name = models.CharField(max_length=255)
    file = models.FileField(upload_to='datasets/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class PromptTemplate(models.Model):
    name = models.CharField(max_length=255)
    template = models.TextField(help_text="Use {{column_name}} placeholders")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class Evaluation(models.Model):
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE)
    prompt_template = models.ForeignKey(PromptTemplate, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

class EvaluationResult(models.Model):
    evaluation = models.ForeignKey(Evaluation, on_delete=models.CASCADE)
    row_index = models.IntegerField()
    llm_name = models.CharField(max_length=100)
    prompt = models.TextField()
    response = models.TextField()
    correctness = models.IntegerField(default=0)
    faithfulness = models.IntegerField(default=0)
