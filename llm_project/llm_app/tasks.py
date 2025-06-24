import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "llm_project.settings")
django.setup()
import logging
logger = logging.getLogger(__name__)
from concurrent.futures import ThreadPoolExecutor
from celery import shared_task
from .models import Evaluation, EvaluationResult
from .utils import call_groq, call_gemini,render_prompt,judge_response,call_together
import pandas as pd
import time
@shared_task
def run_evaluation(evaluation_id):
    start = time.time()
    print(f"🚀 Received task to run evaluation: {evaluation_id}")
    evaluation = Evaluation.objects.get(id=evaluation_id)
    df = pd.read_csv(evaluation.dataset.file)
    template = evaluation.prompt_template.template

    # Full dataset context string (used for every row)
    csv_context = "\n".join([
        ", ".join([f"{col}: {row[col]}" for col in df.columns])
        for _, row in df.iterrows()
    ])

    for i, row in df.iterrows():
        row_data = row.to_dict()
        rendered_prompt = render_prompt(template, row_data)

        final_input = f"""Context:{csv_context}Question:{rendered_prompt}"""

        for llm_name, llm_func in [('together', call_together), ('gemini', call_gemini)]:
            response = llm_func(final_input)
            judgment = judge_response(csv_context, rendered_prompt, response)

            EvaluationResult.objects.create(
                evaluation=evaluation,
                row_index=i,
                llm_name=llm_name,
                prompt=rendered_prompt,
                response=response,
                correctness=judgment.get("correctness", 0),
                faithfulness=judgment.get("faithfulness", 0),
            )
    duration = time.time() - start
    logger.info(f"✅ Evaluation {evaluation_id} completed in {duration:.2f} seconds")


# @shared_task
# def run_evaluation(evaluation_id):
#     start = time.time()
#     print(f"🚀 Starting evaluation {evaluation_id}", flush=True)

#     evaluation = Evaluation.objects.get(id=evaluation_id)
#     df = pd.read_csv(evaluation.dataset.file)
#     template = evaluation.prompt_template.template

#     # Create context string once
#     csv_context = "\n".join([
#         ", ".join([f"{col}: {row[col]}" for col in df.columns])
#         for _, row in df.iterrows()
#     ])

#     results = []

#     for i, row in df.iterrows():
#         row_data = row.to_dict()
#         rendered_prompt = render_prompt(template, row_data)
#         final_input = f"Context:\n{csv_context}\nQuestion:\n{rendered_prompt}"

#         def call_and_judge(llm_name, llm_func):
#             response = llm_func(final_input)
#             judgment = judge_response(csv_context, rendered_prompt, response)
#             return EvaluationResult(
#                 evaluation=evaluation,
#                 row_index=i,
#                 llm_name=llm_name,
#                 prompt=rendered_prompt,
#                 response=response,
#                 correctness=judgment.get("correctness", 0),
#                 faithfulness=judgment.get("faithfulness", 0),
#             )

#         with ThreadPoolExecutor() as executor:
#             futures = {
#                 name: executor.submit(call_and_judge, name, func)
#                 for name, func in [('together', call_together), ('gemini', call_gemini)]
#             }
#             for future in futures.values():
#                 results.append(future.result())

#     # One DB write instead of 1000
#     EvaluationResult.objects.bulk_create(results)

#     print(f"✅ Evaluation {evaluation_id} completed in {time.time() - start:.2f} seconds", flush=True)

# @shared_task
# def run_evaluation(evaluation_id):
#     start = time.time()
#     logger.info(f"🚀 Starting evaluation {evaluation_id}")

#     evaluation = Evaluation.objects.get(id=evaluation_id)
#     df = pd.read_csv(evaluation.dataset.file)
#     template = evaluation.prompt_template.template

#     # Build full context once
#     csv_context = "\n".join([
#         ", ".join([f"{col}: {row[col]}" for col in df.columns])
#         for _, row in df.iterrows()
#     ])

#     # This function processes one row, returns list of EvaluationResult objects
#     def process_row(i, row):
#         row_data = row.to_dict()
#         rendered_prompt = render_prompt(template, row_data)
#         final_input = f"Context:\n{csv_context}\nQuestion:\n{rendered_prompt}"

#         results = []

#         for name, func in [('together', call_together), ('gemini', call_gemini)]:
#             try:
#                 response = func(final_input)
#                 judgment = judge_response(csv_context, rendered_prompt, response)

#                 result = EvaluationResult(
#                     evaluation=evaluation,
#                     row_index=i,
#                     llm_name=name,
#                     prompt=rendered_prompt,
#                     response=response,
#                     correctness=judgment.get("correctness", 0),
#                     faithfulness=judgment.get("faithfulness", 0),
#                 )
#                 results.append(result)
#             except Exception as e:
#                 logger.info(f"⚠️ Error in LLM {name} for row {i}: {e}")

#         return results

#     all_results = []

#     # Process multiple rows in parallel using threads
#     with ThreadPoolExecutor(max_workers=2) as executor:
#         futures = [executor.submit(process_row, i, row) for i, row in df.iterrows()]
#         for future in futures:
#             try:
#                 all_results.extend(future.result())
#             except Exception as e:
#                 logger.info(f"⚠️ Error in row thread: {e}")

#     # One DB write instead of 1000
#     EvaluationResult.objects.bulk_create(all_results)

#     logger.info(f"✅ Evaluation {evaluation_id} completed in {time.time() - start:.2f}s")