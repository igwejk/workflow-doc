FROM python:3.12-alpine

ENV WORKSPACE=/workspace
ENV PATH="${WORKSPACE}:${PATH}"

COPY requirements.txt   "${WORKSPACE}/requirements.txt"
COPY workflowdoc.py     "${WORKSPACE}/workflowdoc.py"

RUN chmod +x    "${WORKSPACE}/workflowdoc.py"                               \
    &&  apk update                                                          \
    &&  apk upgrade                                                         \
    &&  python -m pip install --requirement "${WORKSPACE}/requirements.txt"

WORKDIR "${WORKSPACE}"

ENTRYPOINT [ "workflowdoc.py" ]
CMD [ "--help" ]