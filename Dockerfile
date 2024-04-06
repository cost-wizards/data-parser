FROM public.ecr.aws/lambda/python:3.10

WORKDIR ${LAMBDA_TASK_ROOT}

RUN python3 -m ensurepip

COPY . ${LAMBDA_TASK_ROOT}

RUN pip install -r requirements.txt

CMD ["main.py"]
